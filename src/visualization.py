"""
Chart factory — clean, vibrant, editorial style.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from src.utils import C, FONT


def _layout(title: str, note: str = "") -> dict:
    full = f"<b>{title}</b>"
    if note:
        full += f"<br><span style='font-size:11px;color:{C['subtle']};font-weight:400'>{note}</span>"
    return dict(
        title=dict(text=full, font=dict(size=15, color=C["ink"], family=FONT), x=0),
        plot_bgcolor=C["white"],
        paper_bgcolor=C["white"],
        hovermode="x unified",
        hoverlabel=dict(bgcolor=C["ink"], font=dict(size=12, color="white", family=FONT),
                        bordercolor=C["ink"]),
        legend=dict(orientation="h", y=1.06, x=0, font=dict(size=11, family=FONT, color=C["slate"]),
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=4, r=12, t=72, b=4),
        font=dict(family=FONT, color=C["slate"]),
        xaxis=dict(showgrid=False, tickfont=dict(size=11), linecolor=C["border"]),
        yaxis=dict(gridcolor="#F1F5F9", tickfont=dict(size=11), zeroline=False),
    )


def gdp_trend(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=df["year"], y=df["gdp_usd_billion"], name="GDP (USD B)",
        marker=dict(color=C["chart_a"], opacity=0.85, line=dict(width=0)),
        hovertemplate="<b>%{x}</b>  GDP: $%{y:.2f}B<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["gdp_growth_pct"], name="Real Growth (%)",
        mode="lines+markers",
        line=dict(color=C["chart_b"], width=2.5),
        marker=dict(size=6, color=C["chart_b"]),
        hovertemplate="<b>%{x}</b>  Growth: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
    fig.update_layout(**_layout("GDP & Real Growth Rate", "USD Billion  ·  Right axis: annual % change  ·  Source: World Bank"))
    fig.update_yaxes(title_text="GDP (USD Billion)", secondary_y=False, gridcolor="#F1F5F9")
    fig.update_yaxes(title_text="Real Growth (%)", secondary_y=True, showgrid=False,
                     zeroline=True, zerolinecolor=C["border"],
                     tickfont=dict(color=C["chart_b"]))
    return fig


def gdp_growth_bar(df: pd.DataFrame) -> go.Figure:
    colors = [C["pos"] if v >= 0 else C["neg"] for v in df["gdp_growth_pct"]]
    fig = go.Figure(go.Bar(
        x=df["year"], y=df["gdp_growth_pct"],
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in df["gdp_growth_pct"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{x}</b>: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=0, line_width=1, line_color=C["border"])
    fig.update_layout(**_layout("Real GDP Growth Rate (%)", "Green = expansion  ·  Red = contraction"))
    return fig


def inflation_trend(df: pd.DataFrame) -> go.Figure:
    avg = df["inflation_pct"].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["inflation_pct"], name="CPI Inflation",
        mode="lines+markers",
        fill="tozeroy", fillcolor="rgba(169,30,46,0.08)",
        line=dict(color=C["chart_b"], width=2.5),
        marker=dict(size=6, color=C["chart_b"]),
        hovertemplate="<b>%{x}</b>: %{y:.1f}%<extra></extra>",
    ))
    fig.add_hline(y=avg, line_dash="dot", line_color=C["subtle"], line_width=1,
                  annotation_text=f"Avg {avg:.1f}%",
                  annotation_font=dict(size=10, color=C["muted"]),
                  annotation_position="right")
    fig.update_layout(**_layout("Consumer Price Inflation (%)", "Annual CPI  ·  NRB target: 5.5–6.5%  ·  Source: NRB / World Bank"))
    return fig


def trade_comparison(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["year"], y=df["imports_usd_million"], name="Imports",
                         marker=dict(color=C["chart_b"], opacity=0.8, line=dict(width=0)),
                         hovertemplate="<b>%{x}</b>  Imports: $%{y:,.0f}M<extra></extra>"))
    fig.add_trace(go.Bar(x=df["year"], y=df["exports_usd_million"], name="Exports",
                         marker=dict(color=C["chart_c"], opacity=0.85, line=dict(width=0)),
                         hovertemplate="<b>%{x}</b>  Exports: $%{y:,.0f}M<extra></extra>"))
    fig.update_layout(**_layout("Imports vs Exports", "USD Million  ·  Source: NRB / World Bank"), barmode="group")
    return fig


def trade_balance_chart(df: pd.DataFrame) -> go.Figure:
    colors = [C["pos"] if v >= 0 else C["neg"] for v in df["trade_balance_usd_million"]]
    fig = go.Figure(go.Bar(
        x=df["year"], y=df["trade_balance_usd_million"],
        marker=dict(color=colors, line=dict(width=0)),
        hovertemplate="<b>%{x}</b>: $%{y:,.0f}M<extra></extra>",
    ))
    fig.add_hline(y=0, line_width=1, line_color=C["slate"])
    fig.update_layout(**_layout("Trade Balance (Exports − Imports)", "Negative = deficit  ·  USD Million"))
    return fig


def trade_composition_pie(df: pd.DataFrame, year: int) -> go.Figure:
    row  = df[df["year"] == year].iloc[0]
    tot  = row["exports_usd_million"] + row["imports_usd_million"]
    fig  = go.Figure(go.Pie(
        labels=["Exports", "Imports"],
        values=[row["exports_usd_million"], row["imports_usd_million"]],
        hole=0.50,
        marker=dict(colors=[C["chart_c"], C["chart_b"]], line=dict(color=C["white"], width=2)),
        textinfo="label+percent",
        textfont=dict(size=12, family=FONT),
        hovertemplate="%{label}: $%{value:,.0f}M<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=f"<b>Trade Mix — {year}</b>", font=dict(size=14, family=FONT), x=0.5),
        annotations=[dict(text=f"${tot/1000:.1f}B", x=0.5, y=0.5,
                          font=dict(size=16, family=FONT, color=C["ink"]), showarrow=False)],
        margin=dict(t=50, b=10, l=10, r=10),
        paper_bgcolor=C["white"], height=330,
        legend=dict(font=dict(size=11, family=FONT)),
    )
    return fig


def remittance_trend(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=df["year"], y=df["remittance_usd_billion"], name="Remittance (USD B)",
        marker=dict(color=C["chart_c"], opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>%{x}</b>  $%{y:.2f}B<extra></extra>",
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df["year"], y=df["remittance_pct_gdp"], name="% of GDP",
        mode="lines+markers",
        line=dict(color=C["chart_d"], width=2.5),
        marker=dict(size=6, color=C["chart_d"]),
        hovertemplate="<b>%{x}</b>  % GDP: %{y:.1f}%<extra></extra>",
    ), secondary_y=True)
    fig.update_layout(**_layout("Remittance Inflows & Share of GDP", "USD Billion  ·  Right axis: % of nominal GDP  ·  Source: NRB"))
    fig.update_yaxes(title_text="Remittance (USD B)", secondary_y=False, gridcolor="#F1F5F9")
    fig.update_yaxes(title_text="% of GDP", secondary_y=True, showgrid=False,
                     tickfont=dict(color=C["chart_d"]))
    return fig


def unemployment_trend(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    pre  = df[df["year"] < 2018]
    post = df[df["year"] >= 2018]
    fig.add_trace(go.Scatter(
        x=pre["year"], y=pre["unemployment_pct"], name="Official narrow (pre-2018)",
        mode="lines+markers",
        line=dict(color=C["subtle"], width=2, dash="dot"),
        marker=dict(size=5),
        hovertemplate="<b>%{x}</b>: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=post["year"], y=post["unemployment_pct"], name="ILO modeled (2018+)",
        mode="lines+markers",
        line=dict(color=C["chart_a"], width=2.5),
        marker=dict(size=7, color=C["chart_a"]),
        hovertemplate="<b>%{x}</b>: %{y:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=2017.5, line_width=1, line_dash="dash", line_color=C["border"])
    fig.add_annotation(x=2018.2, y=12.2, text="ILO methodology adopted",
                       showarrow=False, font=dict(size=9, color=C["muted"], family=FONT), xanchor="left")
    fig.update_layout(**_layout("Unemployment Rate (%)", "Dotted = narrow official  ·  Solid = ILO modeled estimate  ·  Source: CBS / World Bank"))
    return fig


def sector_area_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col, name, color in [
        ("services_pct_gdp",    "Services",    C["chart_a"]),
        ("agriculture_pct_gdp", "Agriculture", C["chart_c"]),
        ("industry_pct_gdp",    "Industry",    C["chart_d"]),
    ]:
        fig.add_trace(go.Scatter(
            x=df["year"], y=df[col], name=name,
            stackgroup="one", line=dict(color=color, width=0.5),
            hovertemplate=f"<b>%{{x}}</b>  {name}: %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(**_layout("GDP Sector Composition", "% share of GDP  ·  Source: CBS / World Bank"))
    return fig


def fdi_trend(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df["year"], y=df["fdi_usd_million"], name="FDI Inflow",
        mode="lines+markers",
        fill="tozeroy", fillcolor="rgba(22,38,62,0.06)",
        line=dict(color=C["chart_a"], width=2.5),
        marker=dict(size=6, color=C["chart_a"]),
        hovertemplate="<b>%{x}</b>: $%{y:.1f}M<extra></extra>",
    ))
    fig.update_layout(**_layout("Foreign Direct Investment Inflows", "USD Million  ·  Source: UNCTAD / NRB"))
    return fig


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    cols = {
        "gdp_growth_pct":      "GDP Growth",
        "inflation_pct":       "Inflation",
        "remittance_pct_gdp":  "Remittance/GDP",
        "unemployment_pct":    "Unemployment",
        "exports_usd_million": "Exports",
        "imports_usd_million": "Imports",
        "fdi_usd_million":     "FDI",
    }
    corr = df[list(cols.keys())].rename(columns=cols).corr().round(2)
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns.tolist(), y=corr.index.tolist(),
        colorscale=[[0, C["neg"]], [0.5, "#F7F9F5"], [1, C["chart_a"]]],
        zmid=0, zmin=-1, zmax=1,
        text=corr.values.round(2), texttemplate="%{text}",
        textfont=dict(size=11, family=FONT),
        hovertemplate="<b>%{y} × %{x}</b><br>r = %{z:.2f}<extra></extra>",
        colorbar=dict(thickness=12, len=0.85, title=dict(text="r")),
    ))
    fig.update_layout(
        title=dict(text="<b>Correlation Matrix</b>",
                   font=dict(size=15, family=FONT, color=C["ink"]), x=0),
        margin=dict(l=120, r=20, t=60, b=120),
        paper_bgcolor=C["white"], plot_bgcolor=C["white"],
        font=dict(family=FONT, size=11), height=460,
    )
    fig.update_xaxes(tickangle=-35)
    return fig
