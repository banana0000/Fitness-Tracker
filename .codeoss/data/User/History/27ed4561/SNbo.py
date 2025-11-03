from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import base64, io, os
from datetime import datetime

# =========================================================
# Setup
# =========================================================
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],
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
# Chart helper
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
    color="dark", dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Insights", href="/insights")),
    ],
)

# =========================================================
# Dashboard
# =========================================================
def dashboard_page(data):
    fig_steps, fig_cal = make_charts(data)
    avg_steps = int(data["Steps"].mean())
    avg_cal = int(data["Calories"].mean())

    return dbc.Container(
        [
            html.H2("📊 Dashboard", className="text-center text-warning my-4"),

            # Buttons
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Button("🔄 Refresh from CSV",
                                   id="refresh-btn",
                                   color="warning",
                                   className="text-dark m-2")),
                    dbc.Col(
                        dcc.Upload(
                            id="upload-data",
                            children=html.Div(["📂 Upload CSV File (Day, Steps, Calories)"]),
                            style={
                                "width": "100%",
                                "height": "80px",
                                "lineHeight": "80px",
                                "borderWidth": "2px",
                                "borderStyle": "dashed",
                                "borderColor": "#ffeb3b",
                                "textAlign": "center",
                                "margin": "5px",
                            },
                            multiple=False,
                        )
                    )
                ],
                className="text-center justify-content-center",
            ),
            html.Div(id="refresh-status", className="text-info text-center mb-4"),

            # Stats
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

            # Charts
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
# Insights
# =========================================================
def insights_page(data):
    yesterday = data.iloc[-1]
    previous = data.iloc[-2]

    diff_steps = yesterday["Steps"] - previous["Steps"]
    diff_cal = yesterday["Calories"] - previous["Calories"]

    if diff_steps > 500:
        msg = "🔥 Yesterday you were more active than before — amazing effort!"
        color = "success"
    elif diff_steps < -500:
        msg = "😴 You slowed down yesterday — maybe take a walk today!"
        color = "danger"
    else:
        msg = "💪 Consistent performance — steady progress!"
        color = "warning"

    fig_steps, _ = make_charts(data)
    return dbc.Container(
        [
            html.H2("💬 Insights & Recommendations", className="text-center text-warning my-4"),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("📅 Yesterday Summary", className="text-warning mb-3"),
                        html.P(f"Day: {yesterday['Day']}", className="text-light"),
                        html.P(f"Steps: {int(yesterday['Steps']):,} ({diff_steps:+})",
                               className="text-light"),
                        html.P(f"Calories: {int(yesterday['Calories']):,} kcal ({diff_cal:+})",
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
# Layout & Routing
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
# Refresh (manual) + Upload callbacks
# =========================================================
@app.callback(
    [Output("memory-data", "data"),
     Output("chart-area", "children"),
     Output("refresh-status", "children")],
    [Input("refresh-btn", "n_clicks"),
     Input("upload-data", "contents")],
    [State("upload-data", "filename")]
)
def refresh_or_upload(n_clicks, contents, filename):
    ctx = dash.callback_context

    trigger = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    if trigger == "upload-data" and contents is not None:
        # Uploaded file
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        try:
            new_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
            new_df["Day"] = pd.Categorical(
                new_df["Day"],
                categories=["Monday", "Tuesday", "Wednesday",
                            "Thursday", "Friday", "Saturday", "Sunday"],
                ordered=True,
            )
            figs = make_charts(new_df)
            charts = dbc.Row([
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[0]))],
                                 className="shadow bg-dark border-warning"), md=6),
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[1]))],
                                 className="shadow bg-dark border-danger"), md=6),
            ])
            return new_df.to_dict("records"), charts, f"✅ Uploaded: {filename}"
        except Exception as e:
            return df.to_dict("records"), None, f"❌ Upload failed: {e}"

    elif trigger == "refresh-btn" and n_clicks:
        # Manual CSV reload
        try:
            new_df = pd.read_csv("data.csv")
            new_df["Day"] = pd.Categorical(
                new_df["Day"],
                categories=["Monday", "Tuesday", "Wednesday",
                            "Thursday", "Friday", "Saturday", "Sunday"],
                ordered=True,
            )
            figs = make_charts(new_df)
            charts = dbc.Row([
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[0]))],
                                 className="shadow bg-dark border-warning"), md=6),
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[1]))],
                                 className="shadow bg-dark border-danger"), md=6),
            ])
            ts = datetime.now().strftime("%H:%M:%S")
            return new_df.to_dict("records"), charts, f"✅ Reloaded data.csv at {ts}"
        except Exception as e:
            return df.to_dict("records"), None, f"❌ Error reading CSV: {e}"

    # Default startup
    figs = make_charts(df)
    charts = dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[0]))],
                         className="shadow bg-dark border-warning"), md=6),
        dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=figs[1]))],
                         className="shadow bg-dark border-danger"), md=6),
    ])
    return df.to_dict("records"), charts, ""

# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)