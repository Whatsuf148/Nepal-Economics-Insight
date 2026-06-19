"""
Nepal Economic Insights Dashboard
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from src.data_processing import load_clean_data, filter_years, latest_row, prev_row
from src.visualization import (
    gdp_trend, gdp_growth_bar, inflation_trend,
    trade_comparison, trade_balance_chart, trade_composition_pie,
    remittance_trend, unemployment_trend, sector_area_chart,
    correlation_heatmap, fdi_trend,
)
from src.utils import C, FONT, format_currency, cagr

st.set_page_config(
    page_title="Nepal Economic Insights",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Stylesheet ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

/* ─── Sidebar ─────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {C['sidebar_from']} 0%, {C['sidebar_to']} 100%);
}}
[data-testid="stSidebar"] * {{ color: #B8CCAE !important; }}
[data-testid="stSidebar"] .s-brand {{
    font-size: 20px; font-weight: 800; color: {C['cream']} !important;
    letter-spacing: -.02em; line-height: 1.25; margin: 4px 0 2px;
}}
[data-testid="stSidebar"] .s-tagline {{
    font-size: 11px; color: #7A9A72 !important;
    margin-bottom: 20px; font-weight: 400;
}}
[data-testid="stSidebar"] .s-label {{
    font-size: 9px; font-weight: 700; letter-spacing: .14em;
    text-transform: uppercase; color: #6A8562 !important; margin-bottom: 8px;
}}
[data-testid="stSidebar"] hr {{ border-color: #3A5530 !important; margin: 16px 0; }}
[data-testid="stSidebar"] .s-src {{
    font-size: 11px; color: #7A9A72 !important; padding: 2px 0; display: block;
}}
[data-testid="stSidebar"] .s-src::before {{
    content: "—  "; color: #4A6A42 !important;
}}
[data-testid="stSidebar"] a.s-src {{
    text-decoration: none; transition: color .15s;
}}
[data-testid="stSidebar"] a.s-src:hover {{
    color: {C['cream']} !important;
}}

/* ─── Main ────────────────────────────────────────────────────────────── */
.main .block-container {{ padding: 1.6rem 2.4rem 3rem; max-width: 1440px; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ─── Page header ─────────────────────────────────────────────────────── */
.ph {{
    border-bottom: 2px solid {C['border']};
    padding-bottom: 16px; margin-bottom: 24px;
}}
.ph-eyebrow {{
    font-size: 10px; font-weight: 700; letter-spacing: .16em;
    text-transform: uppercase; color: {C['green']};
    margin-bottom: 6px;
}}
.ph-title {{
    font-size: 28px; font-weight: 800; color: {C['ink']};
    letter-spacing: -.03em; margin: 0 0 4px; line-height: 1.2;
}}
.ph-sub {{
    font-size: 13px; color: {C['muted']}; font-weight: 400;
}}

/* ─── KPI strip ───────────────────────────────────────────────────────── */
.kpi-strip {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 28px;
}}
.kc {{
    border-radius: 12px; padding: 18px 20px 14px;
    border: 1px solid {C['border']};
    background: {C['white']};
    border-top: 3px solid transparent;
}}
.kc-gold   {{ border-top-color: {C['gold']}; }}
.kc-green  {{ border-top-color: {C['green']}; }}
.kc-forest {{ border-top-color: {C['forest']}; }}
.kc-olive  {{ border-top-color: #8B9E3C; }}
.kc-muted  {{ border-top-color: {C['muted']}; }}

.kpi-label {{
    font-size: 9px; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; color: {C['muted']}; margin-bottom: 8px;
}}
.kpi-value {{
    font-size: 26px; font-weight: 800; letter-spacing: -.03em;
    line-height: 1.1; color: {C['ink']}; margin-bottom: 6px;
}}
.kpi-delta {{ font-size: 11px; color: {C['muted']}; font-weight: 400; }}
.kpi-delta .up {{ color: {C['pos']}; font-weight: 600; }}
.kpi-delta .dn {{ color: {C['neg']}; font-weight: 600; }}
.kpi-sub {{ font-size: 10px; color: {C['subtle']}; margin-top: 4px; }}

/* ─── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0; border-bottom: 2px solid {C['border']}; background: transparent;
}}
.stTabs [data-baseweb="tab"] {{
    font-size: 12px; font-weight: 600; letter-spacing: .02em;
    color: {C['muted']}; padding: 9px 20px;
    background: transparent; border-bottom: 2px solid transparent;
    margin-bottom: -2px; border-radius: 0; transition: color .15s;
}}
.stTabs [aria-selected="true"] {{
    color: {C['forest']} !important;
    border-bottom-color: {C['gold']} !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 20px; }}

/* ─── Stat row ────────────────────────────────────────────────────────── */
.stat-row {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; }}
.stat {{
    flex: 1; min-width: 130px;
    background: {C['surface']}; border-radius: 8px;
    padding: 14px 16px; border: 1px solid {C['border']};
}}
.stat-label {{
    font-size: 9px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: {C['subtle']}; margin-bottom: 5px;
}}
.stat-value {{
    font-size: 22px; font-weight: 800; color: {C['ink']};
    letter-spacing: -.02em; line-height: 1.1;
}}
.stat-sub {{ font-size: 10px; color: {C['muted']}; margin-top: 3px; }}

/* ─── Section header ──────────────────────────────────────────────────── */
.sec {{
    font-size: 10px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: {C['slate']};
    padding: 7px 12px; margin: 24px 0 12px;
    background: {C['surface']}; border-radius: 4px;
    border-left: 3px solid {C['gold']};
}}

/* ─── Note boxes ──────────────────────────────────────────────────────── */
.note {{
    border-radius: 8px; padding: 12px 16px; margin: 10px 0;
    font-size: 13px; line-height: 1.65; color: {C['slate']};
}}
.note b {{ font-weight: 700; color: {C['ink']}; }}
.note-gold   {{ background: #FFFBEA; border: 1px solid #F5E080; }}
.note-green  {{ background: #F0F5EC; border: 1px solid #BFCFB8; }}
.note-slate  {{ background: {C['surface']}; border: 1px solid {C['border']}; }}
.note-warn   {{ background: #FEF3F0; border: 1px solid #F5C4B8; }}

/* ─── Expander ────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    border: 1px solid {C['border']} !important;
    border-radius: 8px !important; box-shadow: none !important;
}}

/* ─── Year pills ──────────────────────────────────────────────────────── */
div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] > div {{
    padding: 0 !important;
}}
.year-row {{ display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }}
.year-label {{
    font-size: 9px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: {C['muted']}; margin-right: 6px;
}}
/* active pill button */
button[data-baseweb="button"].pill-active {{
    background: {C['forest']} !important; color: {C['cream']} !important;
    border: 1px solid {C['forest']} !important;
}}

/* ─── Footer ──────────────────────────────────────────────────────────── */
.footer {{
    margin-top: 48px; padding-top: 14px;
    border-top: 1px solid {C['border']};
    font-size: 11px; color: {C['subtle']};
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 4px;
}}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data():
    return load_clean_data()

df_full = get_data()
YEAR_MIN, YEAR_MAX = int(df_full["year"].min()), int(df_full["year"].max())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <p class="s-brand">Nepal Economic<br>Insights</p>
    <p class="s-tagline">Macroeconomic indicators · 2005–{YEAR_MAX}</p>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<p class="s-label">Year Range</p>', unsafe_allow_html=True)
    year_range = st.slider("", YEAR_MIN, YEAR_MAX, (YEAR_MIN, YEAR_MAX),
                           label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<p class="s-label">Data Sources</p>', unsafe_allow_html=True)
    for src, url in [
        ("World Bank Open Data",        "https://data.worldbank.org/country/nepal"),
        ("Nepal Rastra Bank (NRB)",     "https://www.nrb.org.np/"),
        ("Central Bureau of Statistics","https://censusnepal.cbs.gov.np/"),
        ("IMF World Economic Outlook",  "https://www.imf.org/en/Publications/WEO"),
        ("UNCTAD World Investment Report","https://unctad.org/topic/investment/world-investment-report"),
    ]:
        st.markdown(f'<a class="s-src" href="{url}" target="_blank">{src}</a>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <p class="s-label">Author</p>
    <p style="font-size:13px;font-weight:600;color:#D4E8CC !important;margin:0">Sachin Dhakal</p>
    <p style="font-size:11px;color:#7A9A72 !important;margin:2px 0 0">Data Analyst</p>
    """, unsafe_allow_html=True)

df     = filter_years(df_full, year_range[0], year_range[1])

# ── Selected year (year-pill hover/click) ─────────────────────────────────────
years_in_range = sorted(df["year"].tolist())
if "sel_year" not in st.session_state or st.session_state.sel_year not in years_in_range:
    st.session_state.sel_year = years_in_range[-1]

def _pick(y):
    st.session_state.sel_year = y

def _sel_row(df: pd.DataFrame, year: int) -> pd.Series:
    return df[df["year"] == year].iloc[0]

def _prev_row(df: pd.DataFrame, year: int) -> pd.Series:
    idx = years_in_range.index(year)
    return df[df["year"] == years_in_range[idx - 1]].iloc[0] if idx > 0 else _sel_row(df, year)

sel_yr  = st.session_state.sel_year
latest  = _sel_row(df, sel_yr)
prev    = _prev_row(df, sel_yr)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ph">
  <div class="ph-eyebrow">Nepal · Macroeconomic Overview · {year_range[0]}–{year_range[1]} · Showing {sel_yr}</div>
  <h1 class="ph-title">Economic Indicators Dashboard</h1>
  <p class="ph-sub">GDP, Inflation, Trade, Remittance and Employment — sourced from World Bank, NRB, CBS, IMF</p>
</div>
""", unsafe_allow_html=True)

# ── Year pill selector ────────────────────────────────────────────────────────
st.markdown('<p style="font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;'
            f'color:{C["muted"]};margin-bottom:6px">Select Year</p>', unsafe_allow_html=True)
pill_cols = st.columns(len(years_in_range))
for col, y in zip(pill_cols, years_in_range):
    with col:
        is_active = (y == sel_yr)
        label = str(y)
        if is_active:
            st.markdown(
                f'<div style="background:{C["forest"]};color:{C["cream"]};'
                f'text-align:center;border-radius:6px;padding:5px 0;'
                f'font-size:11px;font-weight:700;cursor:default">{label}</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button(label, key=f"yr_{y}", use_container_width=True):
                _pick(y)
                st.rerun()

# style the plain year buttons to be compact
st.markdown(f"""
<style>
button[kind="secondary"] {{
    padding: 4px 0 !important; font-size: 11px !important;
    font-weight: 500 !important; border-radius: 6px !important;
    border: 1px solid {C['border']} !important;
    color: {C['slate']} !important; background: {C['surface']} !important;
}}
button[kind="secondary"]:hover {{
    border-color: {C['green']} !important; color: {C['green']} !important;
    background: #F0F5EC !important;
}}
</style>
""", unsafe_allow_html=True)

# ── KPI helper ────────────────────────────────────────────────────────────────
def _delta(val, unit="%", invert=False):
    good = (val > 0) if not invert else (val < 0)
    cls  = "up" if good else "dn"
    sym  = "+" if val > 0 else ""
    return f'<span class="{cls}">{sym}{val:.1f}{unit}</span> vs prior year'

gdp_g   = latest["gdp_growth_pct"]
inf_d   = latest["inflation_pct"]  - prev["inflation_pct"]
rem_d   = latest["remittance_usd_billion"] - prev["remittance_usd_billion"]
tb      = latest["trade_balance_usd_million"] / 1000
tb_d    = (latest["trade_balance_usd_million"] - prev["trade_balance_usd_million"]) / 1000
unemp_d = latest["unemployment_pct"] - prev["unemployment_pct"]

# ── KPI cards ─────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-strip">
  <div class="kc kc-green">
    <div class="kpi-label">Nominal GDP</div>
    <div class="kpi-value">{format_currency(latest['gdp_usd_billion'])}</div>
    <div class="kpi-delta">{_delta(gdp_g)} real</div>
    <div class="kpi-sub">USD Billion · {int(sel_yr)}</div>
  </div>
  <div class="kc kc-gold">
    <div class="kpi-label">CPI Inflation</div>
    <div class="kpi-value">{latest['inflation_pct']:.1f}%</div>
    <div class="kpi-delta">{_delta(inf_d, 'pp', invert=True)}</div>
    <div class="kpi-sub">NRB target 5.5–6.5%</div>
  </div>
  <div class="kc kc-forest">
    <div class="kpi-label">Remittance</div>
    <div class="kpi-value">{format_currency(latest['remittance_usd_billion'])}</div>
    <div class="kpi-delta">{_delta(rem_d, 'B')}</div>
    <div class="kpi-sub">{latest['remittance_pct_gdp']:.1f}% of GDP · NRB</div>
  </div>
  <div class="kc kc-olive">
    <div class="kpi-label">Trade Balance</div>
    <div class="kpi-value" style="color:{'#C0392B' if tb<0 else '#467235'}">${abs(tb):.2f}B</div>
    <div class="kpi-delta">{'Deficit' if tb<0 else 'Surplus'} &nbsp; {_delta(tb_d, 'B', invert=True)}</div>
    <div class="kpi-sub">Exports minus Imports</div>
  </div>
  <div class="kc kc-muted">
    <div class="kpi-label">Unemployment</div>
    <div class="kpi-value">{latest['unemployment_pct']:.1f}%</div>
    <div class="kpi-delta">{_delta(-unemp_d)}</div>
    <div class="kpi-sub">ILO modeled · World Bank</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_gdp, tab_inf, tab_trade, tab_rem, tab_emp, tab_sec, tab_data = st.tabs(
    ["GDP", "Inflation", "Trade", "Remittance", "Employment", "Sectors", "Data"]
)

# ══ GDP ═══════════════════════════════════════════════════════════════════════
with tab_gdp:
    g5  = cagr(df["gdp_usd_billion"], min(5,  len(df)-1))
    g10 = cagr(df["gdp_usd_billion"], min(10, len(df)-1))

    st.markdown(f"""
    <div class="stat-row">
      <div class="stat">
        <div class="stat-label">Nominal GDP ({int(latest['year'])})</div>
        <div class="stat-value">{format_currency(latest['gdp_usd_billion'])}</div>
        <div class="stat-sub">{latest['gdp_growth_pct']:+.1f}% real growth</div>
      </div>
      <div class="stat">
        <div class="stat-label">5-Year CAGR</div>
        <div class="stat-value">{g5:.1f}%</div>
        <div class="stat-sub">Nominal USD</div>
      </div>
      <div class="stat">
        <div class="stat-label">10-Year CAGR</div>
        <div class="stat-value">{g10:.1f}%</div>
        <div class="stat-sub">Nominal USD</div>
      </div>
      <div class="stat">
        <div class="stat-label">2026 Forecast</div>
        <div class="stat-value">2.3–3.0%</div>
        <div class="stat-sub">World Bank / IMF projection</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(gdp_trend(df), use_container_width=True)
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
        <div class="stat-label">Current ({int(latest['year'])})</div>
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
        <div class="stat-label">Exports ({int(latest['year'])})</div>
        <div class="stat-value">${latest['exports_usd_million']:,.0f}M</div>
        <div class="stat-sub">{latest['export_growth_pct']:+.1f}% YoY</div>
      </div>
      <div class="stat">
        <div class="stat-label">Imports ({int(latest['year'])})</div>
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
        <div class="stat-label">Inflow ({int(latest['year'])})</div>
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
        <div class="stat-label">Unemployment ({int(latest['year'])})</div>
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
        <div class="stat-label">Services ({int(latest['year'])})</div>
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
        <div class="stat-label">FDI ({int(latest['year'])})</div>
        <div class="stat-value">${latest['fdi_usd_million']:.0f}M</div>
        <div class="stat-sub">UNCTAD / NRB</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(sector_area_chart(df), use_container_width=True)
    st.markdown('<div class="sec">Foreign Direct Investment</div>', unsafe_allow_html=True)
    st.plotly_chart(fdi_trend(df), use_container_width=True)

    st.markdown("""
    <div class="note note-green">
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
    styled = (
        tdf.style
        .format({
            "GDP ($B)":"{:.2f}", "Growth (%)":"{:+.1f}", "Inflation (%)":"{:.1f}",
            "Remittance ($B)":"{:.2f}", "Remit./GDP (%)":"{:.1f}",
            "Exports ($M)":"{:,.0f}", "Imports ($M)":"{:,.0f}",
            "Trade Balance ($M)":"{:,.0f}", "Unemployment (%)":"{:.1f}",
            "FDI ($M)":"{:.1f}", "Fiscal Deficit (%)":"{:.1f}",
        })
        .background_gradient(subset=["Growth (%)"],    cmap="RdYlGn", vmin=-5,  vmax=10)
        .background_gradient(subset=["Inflation (%)"], cmap="YlOrRd", vmin=0,   vmax=15)
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
