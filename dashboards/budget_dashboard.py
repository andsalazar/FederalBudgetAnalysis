"""
Interactive dashboard for Federal Budget & Policy Analysis.

Run with: python -m dashboards.budget_dashboard
Or: python dashboards/budget_dashboard.py
"""

try:
    import dash
    from dash import dcc, html, callback, Input, Output
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    raise ImportError("Install dash and plotly: pip install dash plotly")

import pandas as pd
from src.analysis.policy_impact import load_series, load_multiple_series
from src.utils.config import load_config

config = load_config()

# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    title="Federal Budget Analysis Dashboard",
)

# Series available for selection
SERIES_OPTIONS = [
    {"label": "Federal Deficit (% GDP)", "value": "FYFSGDA188S"},
    {"label": "Federal Debt (% GDP)", "value": "GFDEGDQ188S"},
    {"label": "Federal Receipts", "value": "FGRECPT"},
    {"label": "Federal Expenditures", "value": "FGEXPND"},
    {"label": "Median Household Income", "value": "MEHOINUSA672N"},
    {"label": "Real Disposable Income", "value": "DSPIC96"},
    {"label": "CPI (All Urban)", "value": "CPIAUCSL"},
    {"label": "Unemployment Rate", "value": "UNRATE"},
    {"label": "Trade Balance", "value": "BOPGSTB"},
    {"label": "Imports", "value": "IMPGS"},
    {"label": "Exports", "value": "EXPGS"},
    {"label": "Gini Index", "value": "GINIALLRF"},
]

# Policy events for markers
POLICY_EVENTS = {
    "Reagan ERTA (1981)": "1981-08-13",
    "TRA 1986": "1986-10-22",
    "OBRA 1993": "1993-08-10",
    "Bush EGTRRA (2001)": "2001-06-07",
    "Bush JGTRRA (2003)": "2003-05-28",
    "ACA (2010)": "2010-03-23",
    "TCJA (2017)": "2017-12-22",
    "Tariffs sec 232 (2018)": "2018-03-23",
    "Tariffs sec 301 (2018)": "2018-07-06",
}

app.layout = html.Div([
    html.H1("Federal Budget & Policy Analysis", style={"textAlign": "center"}),
    html.Hr(),

    html.Div([
        html.Div([
            html.Label("Select Data Series:"),
            dcc.Dropdown(
                id="series-selector",
                options=SERIES_OPTIONS,
                value=["FYFSGDA188S", "GFDEGDQ188S"],
                multi=True,
            ),
        ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),

        html.Div([
            html.Label("Show Policy Events:"),
            dcc.Checklist(
                id="policy-events",
                options=[{"label": k, "value": k} for k in POLICY_EVENTS],
                value=["TCJA (2017)", "Tariffs sec 232 (2018)"],
                inline=True,
            ),
        ], style={"width": "48%", "display": "inline-block", "padding": "10px"}),
    ]),

    html.Div([
        html.Label("Date Range:"),
        dcc.RangeSlider(
            id="date-range",
            min=1970, max=2026, step=1,
            marks={y: str(y) for y in range(1970, 2030, 5)},
            value=[1990, 2026],
        ),
    ], style={"padding": "20px"}),

    dcc.Graph(id="main-chart", style={"height": "500px"}),
    html.Hr(),

    html.Div([
        html.H3("Policy Period Comparison"),
        dcc.Dropdown(
            id="comparison-series",
            options=SERIES_OPTIONS,
            value="FYFSGDA188S",
        ),
        dcc.Graph(id="comparison-chart", style={"height": "400px"}),
    ], style={"padding": "20px"}),

], style={"maxWidth": "1200px", "margin": "auto", "fontFamily": "Arial"})


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@callback(
    Output("main-chart", "figure"),
    [Input("series-selector", "value"),
     Input("policy-events", "value"),
     Input("date-range", "value")],
)
def update_main_chart(selected_series, selected_events, date_range):
    if not selected_series:
        return go.Figure()

    start = f"{date_range[0]}-01-01"
    end = f"{date_range[1]}-12-31"

    fig = go.Figure()
    for sid in selected_series:
        series = load_series(sid, start, end)
        if not series.empty:
            label = next((o["label"] for o in SERIES_OPTIONS if o["value"] == sid), sid)
            fig.add_trace(go.Scatter(x=series.index, y=series.values, name=label, mode="lines"))

    # Add policy event lines
    if selected_events:
        for event in selected_events:
            if event in POLICY_EVENTS:
                fig.add_vline(
                    x=POLICY_EVENTS[event],
                    line_dash="dash", line_color="gray", opacity=0.6,
                    annotation_text=event, annotation_position="top",
                )

    fig.update_layout(
        title="Economic Indicators Over Time",
        xaxis_title="Date",
        template="plotly_white",
        hovermode="x unified",
    )
    return fig


@callback(
    Output("comparison-chart", "figure"),
    Input("comparison-series", "value"),
)
def update_comparison_chart(series_id):
    if not series_id:
        return go.Figure()

    policy_periods = config.get("analysis", {}).get("policy_periods", {})
    series = load_series(series_id)

    if series.empty:
        return go.Figure()

    labels = []
    means = []
    for name, period in policy_periods.items():
        start = period.get("start")
        end = period.get("end")
        label = period.get("label", name)
        subset = series.loc[start:end]
        if not subset.empty:
            labels.append(label)
            means.append(subset.mean())

    fig = go.Figure(go.Bar(x=means, y=labels, orientation="h"))
    fig.update_layout(
        title=f"Average {series_id} by Policy Period",
        template="plotly_white",
    )
    return fig


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Starting Federal Budget Analysis Dashboard...")
    print("Open http://127.0.0.1:8050 in your browser")
    app.run(debug=True, port=8050)
