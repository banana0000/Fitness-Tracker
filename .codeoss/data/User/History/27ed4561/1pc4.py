from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import base64, io

# =========================================================
# App setup
# =========================================================
app = Dash(__name__,
           external_stylesheets=[dbc.themes.DARKLY],
           suppress_callback_exceptions=True)
server = app.server

# =========================================================
# Load initial data
# =========================================================
df = pd.read_csv("data.csv")
df["Day"] = pd.Categorical(
    df["Day"],
    categories=["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"],
    ordered=True,
)

# =========================================================
# Helper to create charts
# =========================================================
def make_charts(data):
    fig_steps = px.line(
        data, x="Day", y="Steps", markers=True,
        title="Weekly Step Trend", color_discrete_sequence=["#ffeb3b"]
    )
    fig_steps.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            title_x=0.5,
                            font=dict(color="#fff"))

    fig_cal = px.bar(
        data, x="Day", y="Calories",
        title="Weekly Calories Burned",
        color_discrete_sequence=["#e53935"]
    )
    fig_cal.update_layout(plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)",
                          title_x=0.5,
                          font=dict(color="#fff"))
    return fig_steps, fig_cal


# =========================================================
# Navbar
# =========================================================
navbar = dbc.NavbarSimple(
    brand="🏃 FitTrack Pro",
    color="dark",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Insights", href="/insights")),
    ],
)

# =========================================================
# Dashboard (main page)
# =========================================================
def dashboard_page(data):
    fig_steps, fig_cal = make_charts(data)
    avg_steps = int(data["Steps"].mean())
    avg_cal = int(data["Calories"].mean())

    return dbc.Container(
        [
            html.H2("📊 Dashboard", className="text-center text-warning my-4"),

            # Manual refresh button
            dbc.Row(
                dbc.Col(
                    dbc.Button("🔄 Refresh from CSV",
                               id="refresh-btn",
                               color="warning",
                               className="m-2 text-dark"),
                    width="auto", className="text-center"
                )
            ),

            html.Div(id="refresh-status", className="text-info text-center mb-3"),

            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Average Steps"),
                                dbc.CardBody(
                                    html.H4(f"{avg_steps:,}",
                                            className="text-warning text-center")
                                ),
                            ],
                            className="shadow bg-dark border-warning",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Average Calories"),
                                dbc.CardBody(
                                    html.H4(f"{avg_cal:,} kcal",
                                            className="text-danger text-center")
                                ),
                            ],
                            className="shadow bg-dark border-danger",
                        ),
                        md=6,
                    ),
                ],
                className="mb-4",
            ),

            html.Div(id="chart-area", children=[
                dbc.Row([
                    dbc.Col(
                        dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_steps))],
                                 className="shadow bg-dark border-warning"), md=6),
                    dbc.Col(
                        dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_cal))],
                                 className="shadow bg-dark border-danger"), md=6),
                ])
            ]),
        ],
        fluid=True,
    )


# =========================================================
# Insights page (auto recommendations)
# =========================================================
def insights_page(data):
    yesterday = data.iloc[-1]
    previous = data.iloc[-2]

    diff_steps = yesterday["Steps"] - previous["Steps"]
    diff_cal = yesterday["Calories"] - previous["Calories"]

    if diff_steps > 500:
        msg = "🔥 You were more active than the previous day. Keep it up!"
        color = "success"
    elif diff_steps < -500:
        msg = "😴 Yesterday’s activity was lower. Try to move a bit more today!"
        color = "danger"
    else:
        msg = "💪 Consistent performance — steady progress!"
        color = "warning"

    fig_steps, _ = make_charts(data)
    return dbc.Container(
        [
            html.H2("💬 Daily Insights", className="text-center text-warning my-4"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("📅 Yesterday Summary", className="text-warning mb-3"),
                        html.P(f"Day: {yesterday['Day']}", className="text-light"),
                        html.P(f"Steps: {int(yesterday['Steps']):,} ({diff_steps:+})",
                               className="text-light"),
                        html.P(f"Calories: {int(yesterday['Calories']):,} kcal "
                               f"({diff_cal:+})",
                               className="text-light"),
                        html.Div(msg, className=f"alert alert-{color} mt-3"),
                    ]
                ),
                className="shadow bg-dark border-warning mb-4",
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H5("Weekly Trend Overview", className="text-warning"),
                    dcc.Graph(figure=fig_steps, config={'displayModeBar': False}),
                ]),
                className="shadow bg-dark border-warning",
            ),
        ],
        fluid=True,
    )

# =========================================================
# Master Layout + Routing
# =========================================================
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    dcc.Store(id="memory-data", data=df.to_dict("records")),
    html.Div(id="page-content", className="p-3")
])


@app.callback(Output("page-content", "children"),
              [Input("url", "pathname"), Input("memory-data", "data")])
def routing(pathname, memory_data):
    data = pd.DataFrame(memory_data)
    if pathname == "/insights":
        return insights_page(data)
    else:
        return dashboard_page(data)


# =========================================================
# Manual Refresh Callback
# =========================================================
@app.callback(
    [Output("memory-data", "data"),
     Output("refresh-status", "children"),
     Output("chart-area", "children")],
    Input("refresh-btn", "n_clicks"),
)
def refresh_from_csv(n_clicks):
    if not n_clicks:
        figs = make_charts(df)
        charts = dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[0]))],
                             className="shadow bg-dark border-warning"), md=6),
            dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[1]))],
                             className="shadow bg-dark border-danger"), md=6),
        ])
        return df.to_dict("records"), "", charts

    try:
        new_df = pd.read_csv("data.csv")
        new_df["Day"] = pd.Categorical(
            new_df["Day"],
            categories=["Monday", "Tuesday", "Wednesday", "Thursday",
                        "Friday", "Saturday", "Sunday"],
            ordered=True
        )
        figs = make_charts(new_df)
        charts = dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[0]))],
                             className="shadow bg-dark border-warning"), md=6),
            dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[1]))],
                             className="shadow bg-dark border-danger"), md=6),
        ])
        return new_df.to_dict("records"), "✅ Data reloaded from CSV!", charts
    except Exception as e:
        return df.to_dict("records"), f"❌ Error loading CSV: {e}", None


# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)