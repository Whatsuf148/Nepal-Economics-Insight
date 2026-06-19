"""
Design tokens for Nepal Economic Insights Dashboard.
"""

import pandas as pd

# ── Palette ───────────────────────────────────────────────────────────────────
C = {
    # Sidebar / dark base
    "sidebar_from": "#283F24",
    "sidebar_to":   "#1A2918",

    # Brand palette  (colorhunt #FFBF00 #FFF78D #467235 #283F24)
    "gold":     "#FFBF00",
    "cream":    "#FFF78D",
    "green":    "#467235",
    "forest":   "#283F24",

    # Derived accents
    "gold_dark":  "#C99A00",   # darker gold for text on light bg
    "green_light":"#5C8F46",   # lighter green for hover/active

    # Neutrals
    "ink":      "#1A2010",
    "slate":    "#3A4A35",
    "muted":    "#6B7A62",
    "subtle":   "#9DAF94",
    "border":   "#DDE5D8",
    "surface":  "#F7F9F5",
    "white":    "#FFFFFF",

    # Chart series
    "chart_a":  "#467235",   # green
    "chart_b":  "#FFBF00",   # gold
    "chart_c":  "#283F24",   # forest
    "chart_d":  "#C99A00",   # dark gold
    "chart_e":  "#5C8F46",   # light green

    # Semantic
    "pos":  "#467235",
    "neg":  "#C0392B",
}

FONT = "Inter, 'Helvetica Neue', Arial, sans-serif"


def format_currency(value: float, unit: str = "B", decimals: int = 2) -> str:
    return f"${value:.{decimals}f}B" if unit == "B" else f"${value:,.{decimals}f}M"

def yoy_change(series: pd.Series) -> pd.Series:
    return series.pct_change() * 100

def cagr(series: pd.Series, years: int) -> float:
    if len(series) < years + 1:
        return float("nan")
    return ((series.iloc[-1] / series.iloc[-(years + 1)]) ** (1 / years) - 1) * 100

def trade_balance(e: pd.Series, i: pd.Series) -> pd.Series:
    return e - i

def remittance_to_gdp(r: pd.Series, g: pd.Series) -> pd.Series:
    return (r / g) * 100
