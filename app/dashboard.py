"""
Nepal Economic Insights Dashboard
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from src.data_processing import load_clean_data, filter_years
from src.visualization import (
    gdp_trend, gdp_growth_bar, inflation_trend,
    trade_comparison, trade_balance_chart, trade_composition_pie,
    remittance_trend, unemployment_trend, sector_area_chart,
    correlation_heatmap, fdi_trend,
)
from src.utils import (
    C, FONT, FONT_SERIF, FONT_MONO, format_currency, cagr,
    fiscal_year_label, bs_year_label, sparkline_svg,
)

st.set_page_config(
    page_title="Nepal Economic Insights",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Stylesheet ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Source+Serif+4:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
*, html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

html, body, [data-testid="stAppViewContainer"] {{ background: {C['bg']}; }}
.main .block-container {{ padding: 1.4rem 2.4rem 3rem; max-width: 1460px; background: {C['bg']}; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ─── Sidebar — light, matching site theme ───────────────────────────── */
[data-testid="stSidebar"] {{
    background: {C['surface']};
    border-right: 1px solid {C['border']};
}}
[data-testid="stSidebar"] * {{ color: {C['slate']} !important; }}
[data-testid="stSidebar"] .s-brand {{
    font-family: {FONT_SERIF}; font-size: 20px; font-weight: 700;
    color: {C['navy']} !important; letter-spacing: -.01em; line-height: 1.25; margin: 4px 0 2px;
}}
[data-testid="stSidebar"] .s-tagline {{
    font-size: 11px; color: {C['muted']} !important; margin-bottom: 20px; font-weight: 400;
}}
[data-testid="stSidebar"] .s-label {{
    font-size: 9px; font-weight: 700; letter-spacing: .14em;
    text-transform: uppercase; color: {C['crimson']} !important; margin-bottom: 8px;
}}
[data-testid="stSidebar"] hr {{ border-color: {C['border']} !important; margin: 16px 0; }}
[data-testid="stSidebar"] .s-src {{ font-size: 11px; color: {C['slate']} !important; padding: 2px 0; display: block; text-decoration: none; }}
[data-testid="stSidebar"] .s-src::before {{ content: "—  "; color: {C['subtle']} !important; }}
[data-testid="stSidebar"] a.s-src:hover {{ color: {C['crimson']} !important; }}

/* Slider — match navy/crimson theme */
[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {{
    background-color: {C['crimson']} !important;
    border-color: {C['crimson']} !important;
    box-shadow: 0 0 0 2px rgba(169,30,46,.20) !important;
}}
[data-testid="stSidebar"] [data-testid="stSlider"] div[data-baseweb="slider"] > div > div {{
    background: {C['crimson']} !important;
}}
[data-testid="stSidebar"] [data-testid="stSlider"] div[data-baseweb="slider"] > div:first-child {{
    background: {C['border']} !important;
}}
[data-testid="stSidebar"] [data-testid="stTickBar"] {{ display: none; }}
[data-testid="stSidebar"] [data-testid="stSliderTickBarMin"],
[data-testid="stSidebar"] [data-testid="stSliderTickBarMax"] {{
    font-family: {FONT_MONO}; font-size: 10px; color: {C['muted']} !important;
}}
[data-testid="stSidebar"] [data-baseweb="slider"] [aria-hidden="true"] {{ color: {C['navy']} !important; }}

/* ─── Page header ─────────────────────────────────────────────────────── */
.ph {{ display: flex; justify-content: space-between; align-items: flex-end;
       padding-bottom: 14px; gap: 24px; flex-wrap: wrap; }}
.ph-left {{ display: flex; align-items: center; gap: 14px; }}
.ph-flag {{ flex-shrink: 0; margin-top: 4px; }}
.ph-eyebrow {{
    font-size: 10.5px; font-weight: 600; letter-spacing: .1em;
    text-transform: uppercase; color: {C['muted']}; margin-bottom: 4px;
}}
.ph-title {{
    font-family: {FONT_SERIF}; font-size: 30px; font-weight: 700;
    color: {C['navy']}; letter-spacing: -.01em; margin: 0; line-height: 1.1;
}}
.ph-right {{ text-align: right; }}
.ph-fy {{ font-size: 13px; font-weight: 700; color: {C['ink']}; }}
.ph-bs {{ font-family: {FONT_MONO}; font-size: 11px; color: {C['muted']}; font-weight: 500; }}
.ph-updated {{ font-size: 11px; color: {C['subtle']}; margin-top: 2px; }}
.ph-divider {{ border: none; border-top: 1px solid {C['border']}; margin: 0 0 18px; }}

/* ─── Time range row ──────────────────────────────────────────────────── */
.tr-row {{ display: flex; justify-content: space-between; align-items: center;
           margin-bottom: 18px; flex-wrap: wrap; gap: 10px; }}
.tr-label {{ font-size: 9px; font-weight: 700; letter-spacing: .12em;
             text-transform: uppercase; color: {C['muted']}; margin-right: 8px; }}
.tr-hint {{ font-size: 12px; color: {C['muted']}; display: flex; align-items: center; gap: 6px; margin-bottom: 16px; }}
.tr-dot {{ width: 6px; height: 6px; border-radius: 50%; background: {C['crimson']}; display: inline-block; flex-shrink: 0; }}

/* ─── Buttons (year pills) — unified sizing ──────────────────────────────── */
div[data-testid="stButton"] button {{
    border-radius: 6px !important; border: 1px solid {C['border']} !important;
    background: {C['white']} !important; color: {C['slate']} !important;
    font-family: {FONT_MONO} !important; font-size: 12px !important; font-weight: 600 !important;
    padding: 6px 0 !important; height: 32px !important; min-height: 32px !important;
    line-height: 1 !important; transition: all .15s;
}}
div[data-testid="stButton"] button:hover {{
    border-color: {C['navy']} !important; color: {C['navy']} !important; background: {C['surface']} !important;
}}
div[data-testid="stButton"] button:focus:not(:active) {{
    box-shadow: 0 0 0 2px rgba(22,38,62,.15) !important;
}}

/* ─── KPI cards ───────────────────────────────────────────────────────── */
.kpi-strip {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 26px; }}
.kc {{
    background: {C['white']}; border: 1px solid {C['border']}; border-radius: 10px;
    padding: 14px 16px 12px; position: relative; min-height: 128px;
}}
.kpi-label {{ font-size: 9.5px; font-weight: 700; letter-spacing: .1em;
              text-transform: uppercase; color: {C['muted']}; margin-bottom: 9px; }}
.kpi-value {{ display: flex; align-items: baseline; gap: 3px; margin-bottom: 9px; }}
.kpi-value .num {{ font-family: {FONT_MONO}; font-size: 23px; font-weight: 600; color: {C['ink']}; letter-spacing: -.01em; }}
.kpi-value .unit {{ font-family: {FONT_MONO}; font-size: 12px; font-weight: 500; color: {C['subtle']}; }}
.kpi-delta {{ font-family: {FONT_MONO}; font-size: 11px; color: {C['muted']}; line-height: 1.5; }}
.kpi-delta .arrow.up {{ color: {C['pos']}; font-weight: 700; }}
.kpi-delta .arrow.dn {{ color: {C['crimson']}; font-weight: 700; }}
.kpi-delta .dtxt {{ font-weight: 600; color: {C['ink']}; }}
.kpi-spark {{ position: absolute; right: 14px; bottom: 12px; opacity: .9; }}

/* ─── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{ gap: 0; border-bottom: 1px solid {C['border']}; background: transparent; }}
.stTabs [data-baseweb="tab"] {{
    font-size: 12px; font-weight: 600; letter-spacing: .02em; color: {C['muted']};
    padding: 9px 20px; background: transparent; border-bottom: 2px solid transparent;
    margin-bottom: -1px; border-radius: 0; transition: color .15s;
}}
.stTabs [aria-selected="true"] {{
    color: {C['navy']} !important; border-bottom-color: {C['crimson']} !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 20px; }}

/* ─── Stat row ────────────────────────────────────────────────────────── */
.stat-row {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }}
.stat {{ flex: 1; min-width: 130px; background: {C['surface']}; border-radius: 8px;
         padding: 14px 16px; border: 1px solid {C['border']}; }}
.stat-label {{ font-size: 9px; font-weight: 700; letter-spacing: .1em;
               text-transform: uppercase; color: {C['subtle']}; margin-bottom: 5px; }}
.stat-value {{ font-family: {FONT_MONO}; font-size: 21px; font-weight: 600; color: {C['ink']};
               letter-spacing: -.01em; line-height: 1.1; }}
.stat-sub {{ font-size: 10px; color: {C['muted']}; margin-top: 3px; }}

/* ─── Economy at a glance ─────────────────────────────────────────────── */
.glance {{ background: {C['white']}; border: 1px solid {C['border']}; border-radius: 10px;
           padding: 18px 20px; height: 100%; }}
.glance-title {{ font-family: {FONT_SERIF}; font-size: 16px; font-weight: 700; color: {C['navy']}; margin-bottom: 2px; }}
.glance-sub {{ font-size: 11px; color: {C['muted']}; margin-bottom: 14px; }}
.glance-row {{ display: flex; justify-content: space-between; align-items: baseline;
               padding: 9px 0; border-top: 1px solid {C['border']}; }}
.glance-row:first-of-type {{ border-top: none; }}
.glance-key {{ font-size: 12.5px; color: {C['slate']}; }}
.glance-val {{ font-family: {FONT_MONO}; font-size: 14px; font-weight: 600; color: {C['ink']}; }}
.glance-val.accent {{ color: {C['crimson']}; }}

/* ─── Section header ──────────────────────────────────────────────────── */
.sec {{ font-size: 10px; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
        color: {C['slate']}; padding: 7px 12px; margin: 24px 0 12px;
        background: {C['surface']}; border-radius: 4px; border-left: 3px solid {C['crimson']}; }}

/* ─── Note boxes ──────────────────────────────────────────────────────── */
.note {{ border-radius: 8px; padding: 12px 16px; margin: 10px 0; font-size: 13px;
         line-height: 1.65; color: {C['slate']}; }}
.note b {{ font-weight: 700; color: {C['ink']}; }}
.note-gold  {{ background: #FBF6E6; border: 1px solid #E9D9A0; }}
.note-green {{ background: #EEF3EF; border: 1px solid #BFD2C2; }}
.note-slate {{ background: {C['surface']}; border: 1px solid {C['border']}; }}
.note-warn  {{ background: {C['crimson_lt']}; border: 1px solid #E3B9BD; }}

/* ─── Expander ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {{ border: 1px solid {C['border']} !important; border-radius: 8px !important; box-shadow: none !important; }}

/* ─── Footer ──────────────────────────────────────────────────────────── */
.footer {{ margin-top: 48px; padding-top: 14px; border-top: 1px solid {C['border']};
           font-size: 11px; color: {C['subtle']}; display: flex; justify-content: space-between;
           flex-wrap: wrap; gap: 4px; }}

/* ─── Year pills ──────────────────────────────────────────────────────── */
.year-row-label {{ font-size: 9px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
                    color: {C['muted']}; margin-bottom: 6px; }}

/* ─── Responsive: tablet ──────────────────────────────────────────────── */
@media (max-width: 1100px) {{
    .main .block-container {{ padding: 1.2rem 1.4rem 2.4rem; }}
    .kpi-strip {{ grid-template-columns: repeat(3, 1fr); }}
    .ph-title {{ font-size: 26px; }}
}}

/* ─── Responsive: mobile ──────────────────────────────────────────────── */
@media (max-width: 680px) {{
    .main .block-container {{ padding: 1rem 1rem 2rem; }}
    .ph {{ flex-direction: column; align-items: flex-start; gap: 10px; }}
    .ph-right {{ text-align: left; }}
    .ph-title {{ font-size: 22px; }}
    .ph-eyebrow {{ font-size: 9.5px; }}
    .kpi-strip {{ grid-template-columns: repeat(2, 1fr); gap: 10px; }}
    .kc {{ min-height: 112px; padding: 12px 14px 10px; }}
    .kpi-value .num {{ font-size: 20px; }}
    .kpi-spark {{ display: none; }}
    .stat-row {{ flex-direction: column; }}
    .stat {{ min-width: 0; }}
    .glance {{ margin-top: 14px; }}
    .stTabs [data-baseweb="tab"] {{ padding: 8px 12px; font-size: 11px; }}
    .footer {{ flex-direction: column; align-items: flex-start; }}
}}

@media (max-width: 480px) {{
    .kpi-strip {{ grid-template-columns: repeat(2, 1fr); }}
    .ph-title {{ font-size: 19px; }}
}}
</style>
""", unsafe_allow_html=True)

FLAG_SVG = (
    '<svg width="26" height="32" viewBox="0 0 26 32" xmlns="http://www.w3.org/2000/svg">'
    f'<path d="M2 2 L2 30 L19 21 L9.5 15.5 L19 10 L2 2 Z" '
    f'fill="{C["crimson"]}" stroke="{C["navy"]}" stroke-width="1.6" stroke-linejoin="round"/>'
    '</svg>'
)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data():
    return load_clean_data()

df_full = get_data()
YEAR_MIN, YEAR_MAX = int(df_full["year"].min()), int(df_full["year"].max())

if "yr_range" not in st.session_state:
    st.session_state.yr_range = (YEAR_MIN, YEAR_MAX)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <p class="s-brand">Nepal Economic<br>Insights</p>
    <p class="s-tagline">Macroeconomic indicators · 2005–{YEAR_MAX}</p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<p class="s-label">Year Range</p>', unsafe_allow_html=True)
    year_range = st.slider("", YEAR_MIN, YEAR_MAX, key="yr_range", label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<p class="s-label">Data Sources</p>', unsafe_allow_html=True)
    for src, url in [
        ("World Bank Open Data",          "https://data.worldbank.org/country/nepal"),
        ("Nepal Rastra Bank (NRB)",       "https://www.nrb.org.np/"),
        ("Central Bureau of Statistics",  "https://censusnepal.cbs.gov.np/"),
        ("IMF World Economic Outlook",    "https://www.imf.org/en/Publications/WEO"),
        ("UNCTAD World Investment Report","https://unctad.org/topic/investment/world-investment-report"),
    ]:
        st.markdown(f'<a class="s-src" href="{url}" target="_blank">{src}</a>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <p class="s-label">Developed By </p>
    <p style="font-size:13px;font-weight:600;color:{C['navy']} !important;margin:0">Sachin Dhakal</p>
    <p style="font-size:11px;color:{C['muted']} !important;margin:2px 0 0">Data Analyst</p>
    """, unsafe_allow_html=True)

df = filter_years(df_full, year_range[0], year_range[1])

# ── Selected year (year-pill) ─────────────────────────────────────────────────
years_in_range = sorted(df["year"].tolist())
if "sel_year" not in st.session_state or st.session_state.sel_year not in years_in_range:
    st.session_state.sel_year = years_in_range[-1]

def _sel_row(df: pd.DataFrame, year: int) -> pd.Series:
    return df[df["year"] == year].iloc[0]

def _prev_row(df: pd.DataFrame, year: int) -> pd.Series:
    idx = years_in_range.index(year)
    return df[df["year"] == years_in_range[idx - 1]].iloc[0] if idx > 0 else _sel_row(df, year)

sel_yr = st.session_state.sel_year
latest = _sel_row(df, sel_yr)
prev   = _prev_row(df, sel_yr)

# ── Page header ───────────────────────────────────────────────────────────────
import datetime
today_str = datetime.date.today().strftime("%d %b %Y")

st.markdown(f"""
<div class="ph">
  <div class="ph-left">
    <div class="ph-flag">{FLAG_SVG}</div>
    <div>
      <div class="ph-eyebrow">Federal Democratic Republic of Nepal · Macroeconomic Monitor</div>
      <h1 class="ph-title">Nepal Economic Indicators</h1>
    </div>
  </div>
  <div class="ph-right">
    <div class="ph-fy">Fiscal Year {fiscal_year_label(sel_yr)} <span class="ph-bs">· {bs_year_label(sel_yr)}</span></div>
    <div class="ph-updated">Updated {today_str} · NRB / CBS / MoF</div>
  </div>
</div>
<hr class="ph-divider"/>
""", unsafe_allow_html=True)

# ── Year selector ─────────────────────────────────────────────────────────────
st.markdown(
    '<div class="tr-hint"><span class="tr-dot"></span> Hover any chart for exact figures</div>',
    unsafe_allow_html=True,
)
st.markdown('<p class="year-row-label">Select Year for KPI Snapshot</p>', unsafe_allow_html=True)
pill_cols = st.columns(len(years_in_range))
for col, y in zip(pill_cols, years_in_range):
    with col:
        if y == sel_yr:
            st.markdown(
                f'<div style="background:{C["navy"]};color:{C["bg"]};text-align:center;'
                f'border-radius:6px;padding:6px 0;height:32px;box-sizing:border-box;'
                f'font-family:{FONT_MONO};font-size:12px;font-weight:600;line-height:1.15;'
                f'display:flex;align-items:center;justify-content:center;cursor:default">{y}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(str(y), key=f"yr_{y}", use_container_width=True):
                st.session_state.sel_year = y
                st.rerun()

# ── KPI helpers ───────────────────────────────────────────────────────────────
def _delta_html(val, unit="pp", invert=False, label="vs prior year"):
    good = (val > 0) if not invert else (val < 0)
    arrow_cls = "up" if good else "dn"
    arrow = "▲" if val >= 0 else "▼"
    return (f'<span class="arrow {arrow_cls}">{arrow}</span> '
            f'<span class="dtxt">{abs(val):.1f}{unit}</span> {label}')

def _series_tail(col, n=8):
    return df[col].tail(n).tolist()

gdp_g    = latest["gdp_growth_pct"]
gdp_g_d  = gdp_g - prev["gdp_growth_pct"]
inf_d    = latest["inflation_pct"] - prev["inflation_pct"]
rem_d    = latest["remittance_growth_pct"]
tb       = latest["trade_balance_usd_million"] / 1000
tb_d_pct = ((latest["trade_balance_usd_million"] - prev["trade_balance_usd_million"])
            / abs(prev["trade_balance_usd_million"]) * 100) if prev["trade_balance_usd_million"] else 0
unemp_d  = latest["unemployment_pct"] - prev["unemployment_pct"]
fdi_d    = ((latest["fdi_usd_million"] - prev["fdi_usd_million"]) / prev["fdi_usd_million"] * 100
            ) if prev["fdi_usd_million"] else 0

# ── KPI cards ─────────────────────────────────────────────────────────────────
cards = [
    ("GDP Growth", f"{gdp_g:.1f}", "%", _delta_html(gdp_g_d, "pp"),
     sparkline_svg(_series_tail("gdp_growth_pct"), C["navy"])),
    ("Inflation (CPI)", f"{latest['inflation_pct']:.1f}", "%", _delta_html(inf_d, "pp", invert=True),
     sparkline_svg(_series_tail("inflation_pct"), C["crimson"])),
    ("Remittances", format_currency(latest["remittance_usd_billion"]).replace("$",""), "USD B",
     _delta_html(rem_d, "%"), sparkline_svg(_series_tail("remittance_usd_billion"), C["navy"])),
    ("Trade Balance", f"{abs(tb):.2f}", "USD B",
     f'<span class="arrow {"dn" if tb<0 else "up"}">{"▼" if tb_d_pct<0 else "▲"}</span> '
     f'<span class="dtxt">{abs(tb_d_pct):.1f}%</span> · {"Deficit" if tb<0 else "Surplus"}',
     sparkline_svg(_series_tail("trade_balance_usd_million"), C["crimson"])),
    ("Unemployment", f"{latest['unemployment_pct']:.1f}", "%", _delta_html(-unemp_d, "pp"),
     sparkline_svg(_series_tail("unemployment_pct"), C["navy_lt"])),
    ("FDI Inflow", f"{latest['fdi_usd_million']:.0f}", "USD M", _delta_html(fdi_d, "%"),
     sparkline_svg(_series_tail("fdi_usd_million"), C["gold"])),
]

card_html = '<div class="kpi-strip">'
for label, value, unit, delta_html, spark in cards:
    card_html += f"""
    <div class="kc">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value"><span class="num">{value}</span><span class="unit">{unit}</span></div>
      <div class="kpi-delta">{delta_html}</div>
      <div class="kpi-spark">{spark}</div>
    </div>"""
card_html += "</div>"
st.markdown(card_html, unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_gdp, tab_inf, tab_trade, tab_rem, tab_emp, tab_sec, tab_data = st.tabs(
    ["GDP", "Inflation", "Trade", "Remittance", "Employment", "Sectors", "Data"]
)

# ══ GDP ═══════════════════════════════════════════════════════════════════════
with tab_gdp:
    g5  = cagr(df["gdp_usd_billion"], min(5,  len(df)-1))
    g10 = cagr(df["gdp_usd_billion"], min(10, len(df)-1))
    per_capita = latest["gdp_usd_billion"] / latest["population_million"] * 1000

    c1, c2 = st.columns([2.3, 1])
    with c1:
        st.plotly_chart(gdp_trend(df), use_container_width=True)
    with c2:
        st.markdown(f"""
        <div class="glance">
          <div class="glance-title">Economy at a Glance</div>
          <div class="glance-sub">FY {fiscal_year_label(sel_yr)} estimates</div>
          <div class="glance-row"><span class="glance-key">Nominal GDP</span><span class="glance-val">{format_currency(latest['gdp_usd_billion'])}</span></div>
          <div class="glance-row"><span class="glance-key">GDP per Capita</span><span class="glance-val accent">${per_capita:,.0f}</span></div>
          <div class="glance-row"><span class="glance-key">Population</span><span class="glance-val">{latest['population_million']:.1f}M</span></div>
          <div class="glance-row"><span class="glance-key">5-Year CAGR</span><span class="glance-val">{g5:.1f}%</span></div>
          <div class="glance-row"><span class="glance-key">10-Year CAGR</span><span class="glance-val">{g10:.1f}%</span></div>
          <div class="glance-row"><span class="glance-key">Fiscal Deficit</span><span class="glance-val">{latest['fiscal_deficit_pct_gdp']:.1f}% GDP</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sec">Annual Growth Rate</div>', unsafe_allow_html=True)
    st.plotly_chart(gdp_growth_bar(df), use_container_width=True)

    st.markdown("""
    <div class="note note-warn">
      <b>2026 slowdown (2.3–3.0%):</b> Youth-led protests in September 2025 caused losses
      estimated at 1.3% of GDP and triggered a change in government. Recovery is expected
      as political conditions stabilise in FY2026/27.
    </div>
    <div class="note note-slate">
      <b>FY2016/17 peak (9.0%):</b> Highest growth since 1994, driven by post-earthquake
      reconstruction, improved hydropower output, and a rebound in tourism receipts following
      the 2015 earthquake and Madhesh border disruption.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("GDP data table"):
        st.dataframe(df[["year","gdp_usd_billion","gdp_growth_pct"]].rename(columns={
            "year":"Year","gdp_usd_billion":"GDP (USD B)","gdp_growth_pct":"Growth (%)"
        }).set_index("Year"), use_container_width=True)

# ══ INFLATION ═════════════════════════════════════════════════════════════════
with tab_inf:
    avg_inf  = df["inflation_pct"].mean()
    peak     = df["inflation_pct"].max()
    peak_yr  = int(df.loc[df["inflation_pct"].idxmax(), "year"])

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat">
        <div class="stat-label">Current ({sel_yr})</div>
        <div class="stat-value">{latest['inflation_pct']:.1f}%</div>
        <div class="stat-sub">{inf_d:+.1f}pp vs prior year</div>
      </div>
      <div class="stat">
        <div class="stat-label">Period Average</div>
        <div class="stat-value">{avg_inf:.1f}%</div>
        <div class="stat-sub">{year_range[0]}–{year_range[1]}</div>
      </div>
      <div class="stat">
        <div class="stat-label">All-time Peak</div>
        <div class="stat-value">{peak:.1f}%</div>
        <div class="stat-sub">Recorded in {peak_yr}</div>
      </div>
      <div class="stat">
        <div class="stat-label">NRB Target</div>
        <div class="stat-value">5.5–6.5%</div>
        <div class="stat-sub">Monetary policy band</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(inflation_trend(df), use_container_width=True)

    st.markdown("""
    <div class="note note-gold">
      <b>2009 spike (13.1%):</b> Global food and fuel price shock amplified by Nepal's high
      import dependency on India. Supply-side constraints — limited storage, poor road access
      — intensified the pass-through effect on consumer prices.
    </div>
    <div class="note note-green">
      <b>2025 disinflation (3.0%):</b> Five-year low. Easing global commodity prices, a
      stable NPR, and softer domestic demand contributed. NRB maintained a cautious monetary
      stance throughout FY2024/25. Source: NRB, March 2026.
    </div>
    """, unsafe_allow_html=True)

# ══ TRADE ═════════════════════════════════════════════════════════════════════
with tab_trade:
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat">
        <div class="stat-label">Exports ({sel_yr})</div>
        <div class="stat-value">${latest['exports_usd_million']:,.0f}M</div>
        <div class="stat-sub">{latest['export_growth_pct']:+.1f}% YoY</div>
      </div>
      <div class="stat">
        <div class="stat-label">Imports ({sel_yr})</div>
        <div class="stat-value">${latest['imports_usd_million']:,.0f}M</div>
        <div class="stat-sub">{latest['import_growth_pct']:+.1f}% YoY</div>
      </div>
      <div class="stat">
        <div class="stat-label">Trade Balance</div>
        <div class="stat-value">${latest['trade_balance_usd_million']/1000:.2f}B</div>
        <div class="stat-sub">{'Deficit' if latest['trade_balance_usd_million']<0 else 'Surplus'}</div>
      </div>
      <div class="stat">
        <div class="stat-label">FX Reserves</div>
        <div class="stat-value">$20.4B</div>
        <div class="stat-sub">13+ months import cover · NRB 2026</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])
    with c1:
        st.plotly_chart(trade_comparison(df), use_container_width=True)
    with c2:
        yr = st.selectbox("Year", sorted(df["year"].tolist(), reverse=True), key="pie_yr")
        st.plotly_chart(trade_composition_pie(df, yr), use_container_width=True)

    st.plotly_chart(trade_balance_chart(df), use_container_width=True)

    st.markdown("""
    <div class="note note-gold">
      <b>Structural deficit:</b> Imports consistently exceed exports by 5–15x across the
      study period, driven by energy, machinery, and consumer goods from India and China.
      Remittance inflows remain the primary external offset.
    </div>
    <div class="note note-green">
      <b>2026 export acceleration:</b> Early FY2025/26 data shows merchandise exports
      doubling year-on-year, led by soybean oil (43% share) and jute products. FX reserves
      reached a record $20.41B. Source: NRB, The Himalayan Times.
    </div>
    """, unsafe_allow_html=True)

# ══ REMITTANCE ════════════════════════════════════════════════════════════════
with tab_rem:
    rc     = cagr(df["remittance_usd_billion"], min(10, len(df)-1))
    avg_rp = df["remittance_pct_gdp"].mean()

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat">
        <div class="stat-label">Inflow ({sel_yr})</div>
        <div class="stat-value">{format_currency(latest['remittance_usd_billion'])}</div>
        <div class="stat-sub">{latest['remittance_growth_pct']:+.1f}% YoY</div>
      </div>
      <div class="stat">
        <div class="stat-label">Share of GDP</div>
        <div class="stat-value">{latest['remittance_pct_gdp']:.1f}%</div>
        <div class="stat-sub">Avg {avg_rp:.1f}% over period</div>
      </div>
      <div class="stat">
        <div class="stat-label">10-Year CAGR</div>
        <div class="stat-value">{rc:.1f}%</div>
        <div class="stat-sub">Nominal USD</div>
      </div>
      <div class="stat">
        <div class="stat-label">FY2025/26 Q1</div>
        <div class="stat-value">+35.4%</div>
        <div class="stat-sub">YoY growth · NRB</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(remittance_trend(df), use_container_width=True)

    st.markdown("""
    <div class="note note-green">
      <b>Record milestone (Nov 2025):</b> Monthly remittances exceeded Rs 200 billion for
      the first time. Growth is driven by an expanding diaspora in Gulf states, Malaysia,
      and Japan, and greater use of formal banking channels over informal networks.
      Source: Kathmandu Post.
    </div>
    <div class="note note-gold">
      <b>Dependency risk:</b> Nepal's remittance-to-GDP ratio (~25–30%) is among the
      world's highest, creating structural exposure to destination-country policy shifts,
      global recessions, and currency movements not captured in headline GDP figures.
    </div>
    """, unsafe_allow_html=True)

# ══ EMPLOYMENT ════════════════════════════════════════════════════════════════
with tab_emp:
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat">
        <div class="stat-label">Unemployment ({sel_yr})</div>
        <div class="stat-value">{latest['unemployment_pct']:.1f}%</div>
        <div class="stat-sub">ILO modeled estimate</div>
      </div>
      <div class="stat">
        <div class="stat-label">Youth Unemployment</div>
        <div class="stat-value">~20.8%</div>
        <div class="stat-sub">2024 · World Bank</div>
      </div>
      <div class="stat">
        <div class="stat-label">COVID-19 Peak</div>
        <div class="stat-value">11.4%</div>
        <div class="stat-sub">FY 2019/20</div>
      </div>
      <div class="stat">
        <div class="stat-label">Annual Outmigration</div>
        <div class="stat-value">500K+</div>
        <div class="stat-sub">Labour permits · DoFE</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(unemployment_trend(df), use_container_width=True)

    st.markdown("""
    <div class="note note-slate">
      <b>Methodology break (2018):</b> Nepal adopted the ILO broader definition — including
      time-related underemployment — following the 2017/18 Labour Force Survey. The pre-2018
      dotted series reflects the narrow official definition; cross-period comparisons should
      account for this discontinuity.
    </div>
    <div class="note note-gold">
      <b>Structural underemployment:</b> The ILO rate (~10–11%) captures disguised
      unemployment in subsistence agriculture and the informal sector. Over 500,000 Nepali
      workers seek foreign employment annually, suppressing domestic labour market pressure
      while fuelling remittance growth.
    </div>
    """, unsafe_allow_html=True)

# ══ SECTORS ═══════════════════════════════════════════════════════════════════
with tab_sec:
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat">
        <div class="stat-label">Services ({sel_yr})</div>
        <div class="stat-value">{latest['services_pct_gdp']:.1f}%</div>
        <div class="stat-sub">{latest['services_pct_gdp']-prev['services_pct_gdp']:+.1f}pp vs prior year</div>
      </div>
      <div class="stat">
        <div class="stat-label">Agriculture</div>
        <div class="stat-value">{latest['agriculture_pct_gdp']:.1f}%</div>
        <div class="stat-sub">{latest['agriculture_pct_gdp']-prev['agriculture_pct_gdp']:+.1f}pp vs prior year</div>
      </div>
      <div class="stat">
        <div class="stat-label">Industry</div>
        <div class="stat-value">{latest['industry_pct_gdp']:.1f}%</div>
        <div class="stat-sub">{latest['industry_pct_gdp']-prev['industry_pct_gdp']:+.1f}pp vs prior year</div>
      </div>
      <div class="stat">
        <div class="stat-label">FDI ({sel_yr})</div>
        <div class="stat-value">${latest['fdi_usd_million']:.0f}M</div>
        <div class="stat-sub">UNCTAD / NRB</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(sector_area_chart(df), use_container_width=True)
    st.markdown('<div class="sec">Foreign Direct Investment</div>', unsafe_allow_html=True)
    st.plotly_chart(fdi_trend(df), use_container_width=True)

    st.markdown("""
    <div class="note note-slate">
      <b>Structural shift:</b> Agriculture's GDP share fell from ~39% (2005) to ~24.5%
      (2026) as remittance-funded consumption expanded services — trade, finance, real
      estate, and hospitality. Industry remains at 12–15% due to energy infrastructure gaps.
    </div>
    <div class="note note-warn">
      <b>FDI (2024: $57M):</b> Lowest since 2010 per UNCTAD World Investment Report 2025.
      Policy uncertainty and the 2025 political unrest deterred investors. China leads
      approved FDI (~45%), followed by India (~20%). Source: UNCTAD WIR 2025.
    </div>
    """, unsafe_allow_html=True)

# ══ DATA ══════════════════════════════════════════════════════════════════════
with tab_data:
    st.markdown('<div class="sec">Correlation Matrix</div>', unsafe_allow_html=True)
    st.plotly_chart(correlation_heatmap(df), use_container_width=True)

    st.markdown('<div class="sec">Full Dataset — 2005 to 2026</div>', unsafe_allow_html=True)
    cols = {
        "year":                       "Year",
        "gdp_usd_billion":            "GDP ($B)",
        "gdp_growth_pct":             "Growth (%)",
        "inflation_pct":              "Inflation (%)",
        "remittance_usd_billion":     "Remittance ($B)",
        "remittance_pct_gdp":         "Remit./GDP (%)",
        "exports_usd_million":        "Exports ($M)",
        "imports_usd_million":        "Imports ($M)",
        "trade_balance_usd_million":  "Trade Balance ($M)",
        "unemployment_pct":           "Unemployment (%)",
        "fdi_usd_million":            "FDI ($M)",
        "fiscal_deficit_pct_gdp":     "Fiscal Deficit (%)",
    }
    tdf = df[list(cols.keys())].rename(columns=cols).set_index("Year")

    def _gradient(series: pd.Series, lo_rgb, hi_rgb, vmin: float, vmax: float):
        styles = []
        rng = (vmax - vmin) or 1
        for v in series:
            t = max(0.0, min(1.0, (v - vmin) / rng))
            r = round(lo_rgb[0] + (hi_rgb[0] - lo_rgb[0]) * t)
            g = round(lo_rgb[1] + (hi_rgb[1] - lo_rgb[1]) * t)
            b = round(lo_rgb[2] + (hi_rgb[2] - lo_rgb[2]) * t)
            styles.append(f"background-color: rgb({r},{g},{b})")
        return styles

    styled = (
        tdf.style
        .format({
            "GDP ($B)":"{:.2f}", "Growth (%)":"{:+.1f}", "Inflation (%)":"{:.1f}",
            "Remittance ($B)":"{:.2f}", "Remit./GDP (%)":"{:.1f}",
            "Exports ($M)":"{:,.0f}", "Imports ($M)":"{:,.0f}",
            "Trade Balance ($M)":"{:,.0f}", "Unemployment (%)":"{:.1f}",
            "FDI ($M)":"{:.1f}", "Fiscal Deficit (%)":"{:.1f}",
        })
        .apply(_gradient, lo_rgb=(248,113,113), hi_rgb=(134,239,172), vmin=-5, vmax=10, subset=["Growth (%)"])
        .apply(_gradient, lo_rgb=(254,249,195), hi_rgb=(248,113,113), vmin=0,  vmax=15, subset=["Inflation (%)"])
        .set_properties(**{"font-size": "12px"})
    )
    st.dataframe(styled, use_container_width=True, height=500)
    st.download_button(
        "Download CSV",
        data=tdf.to_csv(),
        file_name="nepal_economic_indicators_2005_2026.csv",
        mime="text/csv",
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer">
  <span>Nepal Economic Insights · Sachin Dhakal</span>
  <span>Sources: World Bank · NRB · CBS · IMF · UNCTAD · Data updated June {YEAR_MAX}</span>
</div>
""", unsafe_allow_html=True)
