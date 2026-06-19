"""
Data loading, cleaning, and derived-metric computation.
All transformation logic lives here; the dashboard stays clean.
"""

from pathlib import Path
import pandas as pd
import numpy as np

from src.utils import yoy_change, trade_balance, remittance_to_gdp

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_PATH = DATA_DIR / "raw_data.csv"
CLEAN_PATH = DATA_DIR / "cleaned_data.csv"


# ── Loading ───────────────────────────────────────────────────────────────────

def load_raw() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH)
    df["year"] = df["year"].astype(int)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns and fill structural gaps."""
    df = df.copy()
    df = df.sort_values("year").reset_index(drop=True)
    df = df.drop_duplicates(subset="year")

    # Interpolate any missing numeric values linearly
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols.remove("year")
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear", limit_direction="both")

    df.to_csv(CLEAN_PATH, index=False)
    return df


def add_derived_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute derived columns used across charts."""
    df = df.copy()

    df["trade_balance_usd_million"] = trade_balance(
        df["exports_usd_million"], df["imports_usd_million"]
    )
    df["remittance_pct_gdp"] = remittance_to_gdp(
        df["remittance_usd_billion"], df["gdp_usd_billion"]
    )
    df["export_growth_pct"] = yoy_change(df["exports_usd_million"])
    df["import_growth_pct"] = yoy_change(df["imports_usd_million"])
    df["remittance_growth_pct"] = yoy_change(df["remittance_usd_billion"])
    df["gdp_growth_yoy"] = yoy_change(df["gdp_usd_billion"])   # nominal YoY

    return df


def load_clean_data() -> pd.DataFrame:
    """Main entry point: load → clean → derive → return."""
    df = load_raw()
    df = clean(df)
    df = add_derived_metrics(df)
    return df


# ── Filter helpers ─────────────────────────────────────────────────────────────

def filter_years(df: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    return df[(df["year"] >= start) & (df["year"] <= end)].reset_index(drop=True)


def latest_row(df: pd.DataFrame) -> pd.Series:
    return df.iloc[-1]


def prev_row(df: pd.DataFrame) -> pd.Series:
    return df.iloc[-2]
