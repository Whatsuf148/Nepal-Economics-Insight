"""
Reusable Plotly chart factory functions.
Each function returns a go.Figure ready for st.plotly_chart().
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

from src.utils import COLORS, CHART_TEMPLATE


# ── Shared layout helper ──────────────────────────────────────────────────────

def _base_layout(title: str, y_title: str = "", x_title: str = "Year") -> dict:
    return dict(
        title=dict(text=title, font=dict(size=18, color=COLORS["text"]), x=0.02),
        xaxis=dict(title=x_title, showgrid=False, tickfont=dict(size=12)),
        yaxis=dict(title=y_title, gridcolor="#E8ECF0", tickfont=dict(size=12)),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=20, t=70, b=50),
        font=dict(family="Inter, Arial, sans-serif", color=COLORS["text"]),
    )


# ── GDP Charts ────────────────────────────────────────────────────────────────

def gdp_trend(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df["year"], y=df["gdp_usd_billion"],
            name="GDP (USD Billion)",
            marker_color=COLORS["primary"],
            opacity=0.75,
            hovertemplate="<b>%{x}</b><br>GDP: $%{y:.2f}B<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["year"], y=df["gdp_growth_pct"],
            name="Real GDP Growth (%)",
            mode="lines+markers",
            line=dict(color=COLORS["secondary"], width=2.5),
            marker=dict(size=7),
            hovertemplate="<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    fig.update_layout(**_base_layout("Nepal GDP & Growth Rate (2005–2024)"))
    fig.update_yaxes(title_text="GDP (USD Billion)", secondary_y=False)
    fig.update_yaxes(title_text="GDP Growth Rate (%)", secondary_y=True,
                     zeroline=True, zerolinecolor="#AAB0B8")
    return fig


def gdp_growth_bar(df: pd.DataFrame) -> go.Figure:
    colors = [COLORS["positive"] if v >= 0 else COLORS["negative"]
              for v in df["gdp_growth_pct"]]

    fig = go.Figure(
        go.Bar(
            x=df["year"], y=df["gdp_growth_pct"],
            marker_color=colors,
            text=[f"{v:.1f}%" for v in df["gdp_growth_pct"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_width=1.5, line_dash="dot", line_color="#888")
    fig.update_layout(**_base_layout("Real GDP Growth Rate (%)", y_title="Growth (%)"))
    return fig


# ── Inflation ─────────────────────────────────────────────────────────────────

def inflation_trend(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["year"], y=df["inflation_pct"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor=f"rgba(220,20,60,0.12)",
        line=dict(color=COLORS["secondary"], width=2.5),
        marker=dict(size=7, color=COLORS["secondary"]),
        name="Inflation Rate",
        hovertemplate="<b>%{x}</b><br>Inflation: %{y:.1f}%<extra></extra>",
    ))

    avg = df["inflation_pct"].mean()
    fig.add_hline(y=avg, line_dash="dash", line_color=COLORS["neutral"],
                  annotation_text=f"Avg {avg:.1f}%", annotation_position="right")

    fig.update_layout(**_base_layout("Nepal Inflation Rate (2005–2024)", y_title="Inflation (%)"))
    return fig


# ── Trade ─────────────────────────────────────────────────────────────────────

def trade_comparison(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["year"], y=df["imports_usd_million"],
        name="Imports", marker_color=COLORS["negative"], opacity=0.8,
        hovertemplate="<b>%{x}</b><br>Imports: $%{y:,.0f}M<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=df["year"], y=df["exports_usd_million"],
        name="Exports", marker_color=COLORS["positive"], opacity=0.8,
        hovertemplate="<b>%{x}</b><br>Exports: $%{y:,.0f}M<extra></extra>",
    ))

    fig.update_layout(
        **_base_layout("Nepal Trade: Imports vs Exports (2005–2024)", y_title="USD Million"),
        barmode="group",
    )
    return fig


def trade_balance_chart(df: pd.DataFrame) -> go.Figure:
    colors = [COLORS["positive"] if v >= 0 else COLORS["negative"]
              for v in df["trade_balance_usd_million"]]

    fig = go.Figure(go.Bar(
        x=df["year"], y=df["trade_balance_usd_million"],
        marker_color=colors,
        hovertemplate="<b>%{x}</b><br>Balance: $%{y:,.0f}M<extra></extra>",
        name="Trade Balance",
    ))
    fig.add_hline(y=0, line_width=1.5, line_dash="dot", line_color="#888")
    fig.update_layout(**_base_layout("Trade Balance (Exports – Imports)", y_title="USD Million"))
    return fig


def trade_composition_pie(df: pd.DataFrame, year: int) -> go.Figure:
    row = df[df["year"] == year].iloc[0]
    total = row["exports_usd_million"] + row["imports_usd_million"]
    fig = go.Figure(go.Pie(
        labels=["Exports", "Imports"],
        values=[row["exports_usd_million"], row["imports_usd_million"]],
        hole=0.45,
        marker=dict(colors=[COLORS["positive"], COLORS["negative"]]),
        textinfo="label+percent",
        hovertemplate="%{label}: $%{value:,.0f}M<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=f"Trade Composition – {year}", font=dict(size=16), x=0.5),
        annotations=[dict(text=f"${total/1000:.1f}B", x=0.5, y=0.5,
                          font_size=18, showarrow=False)],
        showlegend=True,
        margin=dict(t=60, b=20, l=20, r=20),
        font=dict(family="Inter, Arial, sans-serif"),
    )
    return fig


# ── Remittance ────────────────────────────────────────────────────────────────

def remittance_trend(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=df["year"], y=df["remittance_usd_billion"],
        name="Remittance (USD Billion)",
        marker_color=COLORS["accent"],
        opacity=0.8,
        hovertemplate="<b>%{x}</b><br>Remittance: $%{y:.2f}B<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df["year"], y=df["remittance_pct_gdp"],
        name="% of GDP",
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=7),
        hovertemplate="<b>%{x}</b><br>% GDP: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)

    fig.update_layout(**_base_layout("Remittance Inflows & % of GDP (2005–2024)"))
    fig.update_yaxes(title_text="Remittance (USD Billion)", secondary_y=False)
    fig.update_yaxes(title_text="% of GDP", secondary_y=True)
    return fig


# ── Employment ────────────────────────────────────────────────────────────────

def unemployment_trend(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df["year"], y=df["unemployment_pct"],
        mode="lines+markers+text",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=8, color=COLORS["primary"]),
        text=[f"{v:.1f}%" for v in df["unemployment_pct"]],
        textposition="top center",
        hovertemplate="<b>%{x}</b><br>Unemployment: %{y:.1f}%<extra></extra>",
        name="Unemployment Rate",
    ))
    fig.update_layout(**_base_layout("Nepal Unemployment Rate (2005–2024)", y_title="%"))
    return fig


# ── Sector composition ────────────────────────────────────────────────────────

def sector_area_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col, name, color in [
        ("agriculture_pct_gdp", "Agriculture", "#27AE60"),
        ("industry_pct_gdp", "Industry", COLORS["primary"]),
        ("services_pct_gdp", "Services", COLORS["accent"]),
    ]:
        fig.add_trace(go.Scatter(
            x=df["year"], y=df[col], name=name,
            stackgroup="one",
            line=dict(color=color, width=1),
            hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(**_base_layout("GDP Sector Composition (%)", y_title="Share of GDP (%)"))
    return fig


# ── Correlation heatmap ───────────────────────────────────────────────────────

def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    cols = {
        "gdp_growth_pct": "GDP Growth",
        "inflation_pct": "Inflation",
        "remittance_pct_gdp": "Remittance/GDP",
        "unemployment_pct": "Unemployment",
        "exports_usd_million": "Exports",
        "imports_usd_million": "Imports",
        "fdi_usd_million": "FDI",
    }
    sub = df[list(cols.keys())].rename(columns=cols)
    corr = sub.corr().round(2)

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=corr.values.round(2),
        texttemplate="%{text}",
        hovertemplate="<b>%{y} × %{x}</b><br>r = %{z:.2f}<extra></extra>",
        colorbar=dict(title="r", tickfont=dict(size=11)),
    ))
    fig.update_layout(
        title=dict(text="Economic Indicators – Correlation Matrix",
                   font=dict(size=18, color=COLORS["text"]), x=0.02),
        margin=dict(l=140, r=20, t=70, b=100),
        font=dict(family="Inter, Arial, sans-serif"),
        paper_bgcolor="white",
    )
    return fig


# ── FDI ──────────────────────────────────────────────────────────────────────

def fdi_trend(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df["year"], y=df["fdi_usd_million"],
        mode="lines+markers",
        fill="tozeroy",
        fillcolor=f"rgba(0,56,147,0.12)",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=7),
        hovertemplate="<b>%{x}</b><br>FDI: $%{y:.1f}M<extra></extra>",
        name="FDI Inflow",
    ))
    fig.update_layout(**_base_layout("Foreign Direct Investment Inflows (USD Million)",
                                     y_title="USD Million"))
    return fig
