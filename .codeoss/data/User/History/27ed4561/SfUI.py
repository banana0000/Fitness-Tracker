from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import base64, io

# =========================================================
# Setup
# =========================================================
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],
           suppress_callback_exceptions=True)
server = app.server

# =========================================================
# Helper: create charts
# =========================================================
def make_charts(data):
    fig_steps = px.line(
        data, x="Day", y="Steps", markers=True,
        title="Weekly Step Count", color_discrete_sequence=["#ffeb3b"]
    )
    fig_steps.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_x=0.5, font=dict(color="#fff")
    )

    fig_cal = px.bar(
        data, x="Day", y="Calories",
        title="Weekly Calories Burned",
        color_discrete_sequence=["#e53935"]
    )
    fig_cal.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_x=0.5, font=dict(color="#fff")
    )
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
# Dashboard
# =========================================================
def dashboard_page(data):
    # If no data provided
    if data is None or len(data) == 0:
        return dbc.Container(
            [
                html.H2("📊 Dashboard", className="text-center text-warning my-4"),
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H5("📂 Upload CSV below",
                                    className="text-warning mb-3 text-center"),
                            html.P(
                                "Please upload a CSV file (Day, Steps, Calories) to display charts.",
                                className="text-center text-light"),
                            dcc.Upload(
                                id="upload-data",
                                children=html.Div(["Drag & Drop or ", html.A("Select file")]),
                                style={
                                    "width": "100%",
                                    "height": "100px",
                                    "lineHeight": "100px",
                                    "borderWidth": "2px",
                                    "borderStyle": "dashed",
                                    "borderColor": "#ffeb3b",
                                    "textAlign": "center",
                                },
                                multiple=False,
                            ),
                            html.Div(id="upload-status", className="text-info text-center mt-3"),
                        ]
                    ),
                    className="shadow bg-dark border-warning",
                ),
            ],
            fluid=True,
        )

    # if file uploaded
    df = pd.DataFrame(data)
    fig_steps, fig_cal = make_charts(df)
    avg_steps = int(df["Steps"].mean())
    avg_cal = int(df["Calories"].mean())

    return dbc.Container(
        [
            html.H2("📊 Dashboard", className="text-center text-warning my-4"),
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
                        ), md=6,
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
                        ), md=6,
                    ),
                ], className="mb-4",
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H5("📂 Upload new CSV", className="text-warning"),
                    html.P("Choose a CSV file with columns: Day, Steps, Calories",
                           className="text-light"),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(["Drag & Drop or ", html.A("Select file")]),
                        style={
                            "width": "100%",
                            "height": "80px",
                            "lineHeight": "80px",
                            "borderWidth": "2px",
                            "borderStyle": "dashed",
                            "borderColor": "#ffeb3b",
                            "textAlign": "center",
                            "marginBottom": "15px",
                        },
                        multiple=False,
                    ),
                    html.Div(id="upload-status", className="text-info"),
                ]),
                className="shadow bg-dark border-warning mb-4"
            ),
            dbc.Row([
                dbc.Col(
                    dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_steps))],
                             className="shadow bg-dark border-warning"), md=6),
                dbc.Col(
                    dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_cal))],
                             className="shadow bg-dark border-danger"), md=6),
            ]),
        ],
        fluid=True,
    )

# =========================================================
# Insights
# =========================================================
def insights_page(data):
    if data is None or len(data) == 0:
        return dbc.Container(
            [
                html.H2("💬 Insights", className="text-center text-warning my-4"),
                dbc.Card(
                    dbc.CardBody(
                        html.P(
                            "No data available. Please upload a CSV first on the Dashboard.",
                            className="text-center text-light"
                        )
                    ),
                    className="shadow bg-dark border-warning"
                ),
            ], fluid=True
        )

    df = pd.DataFrame(data)
    yesterday = df.iloc[-1]
    previous = df.iloc[-2]

    diff_steps = yesterday["Steps"] - previous["Steps"]
    diff_cal = yesterday["Calories"] - previous["Calories"]

    if diff_steps > 500:
        msg = "🔥 Great job! You were more active yesterday!"
        color = "success"
    elif diff_steps < -500:
        msg = "😴 You slowed down — take a short walk today!"
        color = "danger"
    else:
        msg = "💪 Consistent performance — keep the balance."
        color = "warning"

    fig_steps, _ = make_charts(df)
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
        ], fluid=True
    )

# =========================================================
# App layout & routing
# =========================================================
app.layout = html.Div([
    dcc.Location(id="url"),
    navbar,
    dcc.Store(id="memory-data", data=[]),  # start empty
    html.Div(id="page-content", className="p-3")
])

@app.callback(Output("page-content", "children"),
              [Input("url", "pathname"), Input("memory-data", "data")])
def routing(pathname, memory_data):
    if pathname == "/insights":
        return insights_page(memory_data)
    else:
        return dashboard_page(memory_data)

# =========================================================
# Upload callback
# =========================================================
@app.callback(
    [Output("memory-data", "data"),
     Output("upload-status", "children")],
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
)
def upload_csv(contents, filename):
    if contents is None:
        return [], ""
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        new_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        new_df["Day"] = pd.Categorical(
            new_df["Day"],
            categories=["Monday", "Tuesday", "Wednesday", "Thursday",
                        "Friday", "Saturday", "Sunday"],
            ordered=True,
        )
        return new_df.to_dict("records"), f"✅ Uploaded {filename} ({len(new_df)} rows)"
    except Exception as e:
        return [], f"❌ Error loading file: {e}"

# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)