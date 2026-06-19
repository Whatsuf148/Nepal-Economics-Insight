"""
Data loading, cleaning, and derived-metric computation.
"""

from pathlib import Path
import pandas as pd
import numpy as np

from src.utils import yoy_change, trade_balance, remittance_to_gdp

DATA_DIR  = Path(__file__).resolve().parent.parent / "data"
RAW_PATH  = DATA_DIR / "raw_data.csv"
CLEAN_PATH = DATA_DIR / "cleaned_data.csv"


def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH)
    df["year"] = df["year"].astype(int)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy().sort_values("year").drop_duplicates("year").reset_index(drop=True)
    nums = [c for c in df.select_dtypes(include=[np.number]).columns if c != "year"]
    df[nums] = df[nums].interpolate(method="linear", limit_direction="both")
    df.to_csv(CLEAN_PATH, index=False)
    return df


def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["trade_balance_usd_million"] = trade_balance(df["exports_usd_million"], df["imports_usd_million"])
    df["remittance_pct_gdp"]        = remittance_to_gdp(df["remittance_usd_billion"], df["gdp_usd_billion"])
    df["export_growth_pct"]         = yoy_change(df["exports_usd_million"])
    df["import_growth_pct"]         = yoy_change(df["imports_usd_million"])
    df["remittance_growth_pct"]     = yoy_change(df["remittance_usd_billion"])
    return df


def load_clean_data() -> pd.DataFrame:
    return add_derived(clean(load_raw()))


def filter_years(df: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    return df[(df["year"] >= start) & (df["year"] <= end)].reset_index(drop=True)


def latest_row(df: pd.DataFrame) -> pd.Series:
    return df.iloc[-1]


def prev_row(df: pd.DataFrame) -> pd.Series:
    return df.iloc[-2]
