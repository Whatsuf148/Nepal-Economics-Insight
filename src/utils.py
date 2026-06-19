"""
Utility functions for Nepal Economic Insights Dashboard.
"""

import pandas as pd


# ── Color palette ────────────────────────────────────────────────────────────
COLORS = {
    "primary": "#003893",      # Nepal flag blue
    "secondary": "#DC143C",    # Nepal flag red
    "accent": "#FFD700",       # Gold
    "positive": "#27AE60",
    "negative": "#E74C3C",
    "neutral": "#95A5A6",
    "text": "#2C3E50",
    "background": "#F8F9FA",
}

CHART_TEMPLATE = "plotly_white"


def format_currency(value: float, unit: str = "B", decimals: int = 2) -> str:
    """Return a human-readable currency string."""
    if unit == "B":
        return f"${value:.{decimals}f}B"
    if unit == "M":
        return f"${value:.{decimals}f}M"
    return f"${value:.{decimals}f}"


def format_pct(value: float, decimals: int = 1) -> str:
    return f"{value:+.{decimals}f}%"


def yoy_change(series: pd.Series) -> pd.Series:
    """Year-over-year percentage change."""
    return series.pct_change() * 100


def cagr(series: pd.Series, years: int) -> float:
    """Compound annual growth rate over the last `years` years."""
    if len(series) < years + 1:
        return float("nan")
    end = series.iloc[-1]
    start = series.iloc[-(years + 1)]
    return ((end / start) ** (1 / years) - 1) * 100


def delta_arrow(value: float) -> str:
    """Return an arrow emoji indicating direction."""
    if value > 0:
        return "▲"
    if value < 0:
        return "▼"
    return "—"


def trade_balance(exports: pd.Series, imports: pd.Series) -> pd.Series:
    """Compute trade balance (exports – imports)."""
    return exports - imports


def remittance_to_gdp(remittance_bn: pd.Series, gdp_bn: pd.Series) -> pd.Series:
    """Remittance as % of GDP."""
    return (remittance_bn / gdp_bn) * 100
