"""
Design tokens for Nepal Economic Insights Dashboard.
"""

import pandas as pd

# ── Palette ───────────────────────────────────────────────────────────────────
# Editorial style: cream page, navy ink, crimson accent (Nepal flag colors).
C = {
    # Sidebar / dark base
    "sidebar_from": "#16263E",
    "sidebar_to":   "#0E1A2C",

    # Brand palette
    "navy":     "#16263E",
    "navy_lt":  "#3B5374",
    "crimson":  "#A91E2E",
    "crimson_lt": "#FBEAEA",
    "gold":     "#C9A227",

    # Neutrals
    "ink":      "#1A2230",
    "slate":    "#46506A",
    "muted":    "#8A8F9C",
    "subtle":   "#B7BBC4",
    "border":   "#E4E1D8",
    "surface":  "#F4F2EC",
    "bg":       "#FAF8F4",
    "white":    "#FFFFFF",

    # Chart series
    "chart_a":  "#16263E",   # navy
    "chart_b":  "#A91E2E",   # crimson
    "chart_c":  "#3B5374",   # navy light
    "chart_d":  "#C9A227",   # gold
    "chart_e":  "#8A8F9C",   # muted gray

    # Semantic
    "pos":  "#1E7A4C",
    "neg":  "#A91E2E",
}

FONT       = "Inter, 'Helvetica Neue', Arial, sans-serif"
FONT_SERIF = "'Source Serif 4', Georgia, 'Times New Roman', serif"
FONT_MONO  = "'IBM Plex Mono', 'Courier New', monospace"


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

def fiscal_year_label(year: int) -> str:
    return f"{year - 1}/{str(year)[-2:]}"

def bs_year_label(year: int) -> str:
    bs_start = year + 56
    return f"{bs_start}/{str(bs_start + 1)[-2:]} BS"

def sparkline_svg(values, color: str = "#16263E", width: int = 72, height: int = 26) -> str:
    vals = [v for v in values if pd.notna(v)]
    if len(vals) < 2:
        return ""
    vmin, vmax = min(vals), max(vals)
    rng = (vmax - vmin) or 1
    n = len(vals)
    pts = []
    for i, v in enumerate(vals):
        x = i / (n - 1) * width
        y = height - ((v - vmin) / rng) * (height - 4) - 2
        pts.append(f"{x:.1f},{y:.1f}")
    points = " ".join(pts)
    return (
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'style="display:block" preserveAspectRatio="none">'
        f'<polyline points="{points}" fill="none" stroke="{color}" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )
