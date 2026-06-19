"""
Nepal Economic Insights Dashboard
Main Streamlit application entry point.
"""

import sys
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd

from src.data_processing import load_clean_data, filter_years, latest_row, prev_row
from src.visualization import (
    gdp_trend,
    gdp_growth_bar,
    inflation_trend,
    trade_comparison,
    trade_balance_chart,
    trade_composition_pie,
    remittance_trend,
    unemployment_trend,
    sector_area_chart,
    correlation_heatmap,
    fdi_trend,
)
from src.utils import COLORS, format_currency, format_pct, cagr, delta_arrow


# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Nepal Economic Insights",
    page_icon="🇳🇵",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #003893 0%, #002560 100%);
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stSlider > div > div > div { background: #DC143C; }

    /* KPI cards */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 18px 22px;
        border-left: 5px solid #003893;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 8px;
    }
    .kpi-label  { font-size: 12px; font-weight: 600; color: #7F8C8D; text-transform: uppercase; letter-spacing: .06em; }
    .kpi-value  { font-size: 28px; font-weight: 700; color: #003893; margin: 4px 0; }
    .kpi-delta  { font-size: 13px; font-weight: 500; }
    .kpi-delta.pos { color: #27AE60; }
    .kpi-delta.neg { color: #E74C3C; }

    /* Section headers */
    .section-header {
        font-size: 20px; font-weight: 700; color: #003893;
        border-bottom: 2px solid #DC143C;
        padding-bottom: 6px; margin: 32px 0 16px;
    }

    /* Tab style */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        padding: 8px 20px;
    }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Data ──────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def get_data() -> pd.DataFrame:
    return load_clean_data()


df_full = get_data()
YEAR_MIN = int(df_full["year"].min())
YEAR_MAX = int(df_full["year"].max())


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Flag_of_Nepal.svg/200px-Flag_of_Nepal.svg.png",
        width=60,
    )
    st.markdown("## 🇳🇵 Nepal Economic Insights")
    st.markdown("---")

    st.markdown("### Filters")
    year_range = st.slider(
        "Year Range",
        min_value=YEAR_MIN,
        max_value=YEAR_MAX,
        value=(YEAR_MIN, YEAR_MAX),
        step=1,
    )

    st.markdown("---")
    st.markdown("### Data Sources")
    st.markdown("""
- World Bank Open Data
- Nepal Rastra Bank (NRB)
- Central Bureau of Statistics
- IMF World Economic Outlook
    """)
    st.markdown("---")
    st.caption("Dashboard by **Sachin Dhakal**  \nAspiring Data Analyst")


df = filter_years(df_full, year_range[0], year_range[1])
latest = latest_row(df)
prev = prev_row(df) if len(df) > 1 else latest


# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<h1 style='color:#003893; font-size:36px; font-weight:800; margin-bottom:4px;'>
    🇳🇵 Nepal Economic Insights Dashboard
</h1>
<p style='color:#555; font-size:15px; margin-top:0;'>
    Macroeconomic performance • GDP • Trade • Remittance • Inflation • Employment
</p>
""", unsafe_allow_html=True)

st.markdown(f"**Showing data:** {year_range[0]} – {year_range[1]}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Latest year:** {int(latest['year'])}&nbsp;&nbsp;|&nbsp;&nbsp;"
            f"**Source:** World Bank · NRB · CBS · IMF")

st.markdown("---")


# ── KPI Cards ─────────────────────────────────────────────────────────────────

def kpi_card(label: str, value: str, delta: float, delta_label: str = "vs prev year") -> str:
    arrow = delta_arrow(delta)
    cls = "pos" if delta >= 0 else "neg"
    delta_str = format_pct(delta) if delta != 0 else "—"
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta {cls}">{arrow} {delta_str} {delta_label}</div>
    </div>
    """


gdp_delta = latest["gdp_usd_billion"] - prev["gdp_usd_billion"]
inf_delta = latest["inflation_pct"] - prev["inflation_pct"]
rem_delta = latest["remittance_usd_billion"] - prev["remittance_usd_billion"]
trade_delta = latest["trade_balance_usd_million"] - prev["trade_balance_usd_million"]

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(kpi_card(
        "GDP (USD)", format_currency(latest["gdp_usd_billion"]),
        latest["gdp_growth_pct"], "real growth"
    ), unsafe_allow_html=True)

with col2:
    st.markdown(kpi_card(
        "Inflation Rate", f"{latest['inflation_pct']:.1f}%",
        inf_delta
    ), unsafe_allow_html=True)

with col3:
    st.markdown(kpi_card(
        "Remittance", format_currency(latest["remittance_usd_billion"]),
        rem_delta
    ), unsafe_allow_html=True)

with col4:
    tb = latest["trade_balance_usd_million"] / 1000
    st.markdown(kpi_card(
        "Trade Balance", format_currency(abs(tb)) + (" deficit" if tb < 0 else " surplus"),
        trade_delta / 1000
    ), unsafe_allow_html=True)

with col5:
    st.markdown(kpi_card(
        "Unemployment", f"{latest['unemployment_pct']:.1f}%",
        -(latest["unemployment_pct"] - prev["unemployment_pct"])   # lower = better
    ), unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_gdp, tab_inflation, tab_trade, tab_remittance, tab_employment, tab_sectors, tab_advanced = st.tabs([
    "📈 GDP",
    "💸 Inflation",
    "🌍 Trade",
    "💰 Remittance",
    "💼 Employment",
    "🏭 Sectors",
    "🔬 Advanced",
])


# ─────────────────────────────────────────────────────────────────────────────
# GDP TAB
# ─────────────────────────────────────────────────────────────────────────────

with tab_gdp:
    st.markdown('<div class="section-header">GDP Overview</div>', unsafe_allow_html=True)

    gdp_cagr_5 = cagr(df["gdp_usd_billion"], min(5, len(df) - 1))
    gdp_cagr_10 = cagr(df["gdp_usd_billion"], min(10, len(df) - 1))

    m1, m2, m3 = st.columns(3)
    m1.metric("Latest GDP", format_currency(latest["gdp_usd_billion"]),
              f"{latest['gdp_growth_pct']:+.1f}% real growth")
    m2.metric("5-Year GDP CAGR", f"{gdp_cagr_5:.1f}%" if not pd.isna(gdp_cagr_5) else "—")
    m3.metric("10-Year GDP CAGR", f"{gdp_cagr_10:.1f}%" if not pd.isna(gdp_cagr_10) else "—")

    st.plotly_chart(gdp_trend(df), use_container_width=True)

    st.markdown('<div class="section-header">Real GDP Growth Rate</div>', unsafe_allow_html=True)
    st.plotly_chart(gdp_growth_bar(df), use_container_width=True)

    with st.expander("📋 GDP Data Table"):
        st.dataframe(
            df[["year", "gdp_usd_billion", "gdp_growth_pct"]].rename(columns={
                "year": "Year",
                "gdp_usd_billion": "GDP (USD B)",
                "gdp_growth_pct": "Real Growth (%)",
            }).set_index("Year"),
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# INFLATION TAB
# ─────────────────────────────────────────────────────────────────────────────

with tab_inflation:
    st.markdown('<div class="section-header">Inflation Rate Tracking</div>', unsafe_allow_html=True)

    avg_inf = df["inflation_pct"].mean()
    max_inf = df["inflation_pct"].max()
    max_inf_year = df.loc[df["inflation_pct"].idxmax(), "year"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Current Inflation", f"{latest['inflation_pct']:.1f}%",
              f"{inf_delta:+.1f}pp vs prev year")
    m2.metric("Period Average", f"{avg_inf:.1f}%")
    m3.metric("Peak Inflation", f"{max_inf:.1f}% ({int(max_inf_year)})")

    st.plotly_chart(inflation_trend(df), use_container_width=True)

    st.info(
        "**Key observation:** Nepal's inflation spiked to ~13.1% in 2009 driven by global food "
        "and fuel price shocks. The 2022 spike (7.7%) reflects post-COVID supply-chain disruptions "
        "and the Russia-Ukraine war impact on fuel/food prices."
    )


# ─────────────────────────────────────────────────────────────────────────────
# TRADE TAB
# ─────────────────────────────────────────────────────────────────────────────

with tab_trade:
    st.markdown('<div class="section-header">Import vs Export Analysis</div>', unsafe_allow_html=True)

    total_exports = df["exports_usd_million"].sum()
    total_imports = df["imports_usd_million"].sum()
    avg_deficit = df["trade_balance_usd_million"].mean()

    m1, m2, m3 = st.columns(3)
    m1.metric("Latest Exports", f"${latest['exports_usd_million']:,.0f}M",
              f"{latest['export_growth_pct']:+.1f}% YoY")
    m2.metric("Latest Imports", f"${latest['imports_usd_million']:,.0f}M",
              f"{latest['import_growth_pct']:+.1f}% YoY")
    m3.metric("Trade Balance",
              f"${latest['trade_balance_usd_million']:,.0f}M",
              "Deficit" if latest["trade_balance_usd_million"] < 0 else "Surplus")

    c1, c2 = st.columns([2, 1])
    with c1:
        st.plotly_chart(trade_comparison(df), use_container_width=True)
    with c2:
        pie_year = st.selectbox("Select year for composition",
                                sorted(df["year"].tolist(), reverse=True), key="pie_year")
        st.plotly_chart(trade_composition_pie(df, pie_year), use_container_width=True)

    st.plotly_chart(trade_balance_chart(df), use_container_width=True)

    st.warning(
        "Nepal runs a **persistent trade deficit** — imports consistently exceed exports by 8–15×. "
        "Remittance inflows partially compensate for this structural imbalance."
    )


# ─────────────────────────────────────────────────────────────────────────────
# REMITTANCE TAB
# ─────────────────────────────────────────────────────────────────────────────

with tab_remittance:
    st.markdown('<div class="section-header">Remittance Inflow Analysis</div>', unsafe_allow_html=True)

    rem_cagr = cagr(df["remittance_usd_billion"], min(10, len(df) - 1))
    avg_rem_pct = df["remittance_pct_gdp"].mean()

    m1, m2, m3 = st.columns(3)
    m1.metric("Latest Remittance", format_currency(latest["remittance_usd_billion"]),
              f"{latest['remittance_growth_pct']:+.1f}% YoY")
    m2.metric("Remittance / GDP", f"{latest['remittance_pct_gdp']:.1f}%",
              f"Avg {avg_rem_pct:.1f}%")
    m3.metric("10-Year CAGR", f"{rem_cagr:.1f}%" if not pd.isna(rem_cagr) else "—")

    st.plotly_chart(remittance_trend(df), use_container_width=True)

    st.success(
        "Remittance is Nepal's largest source of foreign exchange, accounting for ~20–30% of GDP. "
        "It funds household consumption, education, and healthcare — acting as a major cushion "
        "against trade deficits."
    )


# ─────────────────────────────────────────────────────────────────────────────
# EMPLOYMENT TAB
# ─────────────────────────────────────────────────────────────────────────────

with tab_employment:
    st.markdown('<div class="section-header">Employment & Unemployment Trends</div>',
                unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Current Unemployment", f"{latest['unemployment_pct']:.1f}%",
              f"{-(latest['unemployment_pct'] - prev['unemployment_pct']):+.1f}pp")
    m2.metric("Peak (COVID-19 2020)", "4.4%")
    m3.metric("Period Low", f"{df['unemployment_pct'].min():.1f}%")

    st.plotly_chart(unemployment_trend(df), use_container_width=True)

    st.info(
        "Nepal's **reported unemployment** is low, but this masks high underemployment and "
        "disguised unemployment in agriculture. Over 500,000 workers emigrate annually for "
        "foreign employment, which is why the formal unemployment figure stays suppressed."
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTORS TAB
# ─────────────────────────────────────────────────────────────────────────────

with tab_sectors:
    st.markdown('<div class="section-header">GDP Sector Composition</div>', unsafe_allow_html=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Agriculture Share", f"{latest['agriculture_pct_gdp']:.1f}%",
              f"{latest['agriculture_pct_gdp'] - prev['agriculture_pct_gdp']:+.1f}pp")
    m2.metric("Industry Share", f"{latest['industry_pct_gdp']:.1f}%",
              f"{latest['industry_pct_gdp'] - prev['industry_pct_gdp']:+.1f}pp")
    m3.metric("Services Share", f"{latest['services_pct_gdp']:.1f}%",
              f"{latest['services_pct_gdp'] - prev['services_pct_gdp']:+.1f}pp")

    st.plotly_chart(sector_area_chart(df), use_container_width=True)

    st.markdown('<div class="section-header">Foreign Direct Investment</div>',
                unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    m1.metric("Latest FDI", f"${latest['fdi_usd_million']:.1f}M",
              f"{latest['fdi_usd_million'] - prev['fdi_usd_million']:+.1f}M vs prev")
    m2.metric("FDI / GDP", f"{(latest['fdi_usd_million'] / (latest['gdp_usd_billion']*1000))*100:.2f}%")
    st.plotly_chart(fdi_trend(df), use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# ADVANCED TAB
# ─────────────────────────────────────────────────────────────────────────────

with tab_advanced:
    st.markdown('<div class="section-header">Correlation Analysis</div>', unsafe_allow_html=True)
    st.plotly_chart(correlation_heatmap(df), use_container_width=True)

    st.markdown('<div class="section-header">Full Dataset</div>', unsafe_allow_html=True)
    display_cols = {
        "year": "Year",
        "gdp_usd_billion": "GDP ($B)",
        "gdp_growth_pct": "GDP Growth (%)",
        "inflation_pct": "Inflation (%)",
        "remittance_usd_billion": "Remittance ($B)",
        "remittance_pct_gdp": "Remittance/GDP (%)",
        "exports_usd_million": "Exports ($M)",
        "imports_usd_million": "Imports ($M)",
        "trade_balance_usd_million": "Trade Balance ($M)",
        "unemployment_pct": "Unemployment (%)",
        "fdi_usd_million": "FDI ($M)",
    }
    styled = (
        df[list(display_cols.keys())]
        .rename(columns=display_cols)
        .set_index("Year")
        .style
        .format({
            "GDP ($B)": "{:.2f}",
            "GDP Growth (%)": "{:+.1f}%",
            "Inflation (%)": "{:.1f}%",
            "Remittance ($B)": "{:.2f}",
            "Remittance/GDP (%)": "{:.1f}%",
            "Exports ($M)": "{:,.0f}",
            "Imports ($M)": "{:,.0f}",
            "Trade Balance ($M)": "{:,.0f}",
            "Unemployment (%)": "{:.1f}%",
            "FDI ($M)": "{:.1f}",
        })
        .background_gradient(subset=["GDP Growth (%)"], cmap="RdYlGn")
        .background_gradient(subset=["Inflation (%)"], cmap="YlOrRd")
    )
    st.dataframe(styled, use_container_width=True)

    st.download_button(
        label="⬇️ Download Dataset (CSV)",
        data=df[list(display_cols.keys())].rename(columns=display_cols).to_csv(index=False),
        file_name="nepal_economic_data.csv",
        mime="text/csv",
    )


# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#999; font-size:13px;'>"
    "Nepal Economic Insights Dashboard · Built by <b>Sachin Dhakal</b> · "
    "Data: World Bank · NRB · CBS · IMF"
    "</div>",
    unsafe_allow_html=True,
)
