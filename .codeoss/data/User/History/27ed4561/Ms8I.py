from dash import Dash, html, dcc, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import io, base64

# ===== Setup =====
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
server = app.server

# ===== Default data =====
df = pd.read_csv("data.csv")
df["Day"] = pd.Categorical(
    df["Day"],
    categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    ordered=True,
)
avg_steps = int(df["Steps"].mean())
avg_cal = int(df["Calories"].mean())

# ===== Helper: create charts =====
def make_charts(data):
    fig_steps = px.line(
        data,
        x="Day",
        y="Steps",
        markers=True,
        title="Weekly Step Count",
        color_discrete_sequence=["#ffeb3b"],
    )
    fig_steps.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fff"),
        title_x=0.5,
    )

    fig_cal = px.bar(
        data,
        x="Day",
        y="Calories",
        title="Calories Burned per Day",
        color_discrete_sequence=["#e53935"],
    )
    fig_cal.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#fff"),
        title_x=0.5,
    )
    return fig_steps, fig_cal


# ===== Navbar =====
navbar = dbc.NavbarSimple(
    brand="🏃 FitTrack Pro",
    color="dark",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Insights", href="/insights")),
        dbc.NavItem(dbc.NavLink("Upload CSV", href="/upload")),
        dbc.NavItem(dbc.NavLink("About", href="/about")),
    ],
)

# ===== Dashboard Page =====
def dashboard_layout(data):
    fig_steps, fig_cal = make_charts(data)
    avg_steps = int(data["Steps"].mean())
    avg_cal = int(data["Calories"].mean())

    return dbc.Container(
        [
            html.H2("📊 Dashboard", className="text-center text-warning my-4"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Average Steps"),
                                dbc.CardBody(html.H4(f"{avg_steps:,}", className="text-warning")),
                            ],
                            className="shadow bg-dark border-warning",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Average Calories"),
                                dbc.CardBody(html.H4(f"{avg_cal:,} kcal", className="text-danger")),
                            ],
                            className="shadow bg-dark border-danger",
                        ),
                        md=6,
                    ),
                ],
                className="mb-3",
            ),
            dbc.Row(
                [
                    dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_steps))],
                                     className="shadow bg-dark border-warning"), md=6),
                    dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_cal))],
                                     className="shadow bg-dark border-danger"), md=6),
                ],
                className="gy-3",
            ),
        ],
        fluid=True,
    )


# ===== Insights Page =====
insights_layout = dbc.Container(
    [
        html.H2("💬 Insights", className="text-center text-warning my-4"),
        dbc.Card(
            dbc.CardBody([
                html.P("Select a day to get personalized advice:",
                       className="lead text-white"),
                dcc.Dropdown(
                    id="day-dropdown",
                    options=[{"label": d, "value": d} for d in df["Day"]],
                    value="Monday",
                    clearable=False,
                    style={"color": "#000"},
                ),
                html.Div(id="advice-output"),
            ]),
            className="shadow bg-dark border-warning",
        ),
    ],
    fluid=True,
)

# ===== Upload Page =====
upload_layout = dbc.Container(
    [
        html.H2("📂 Upload CSV", className="text-center text-warning my-4"),
        dbc.Card(
            dbc.CardBody(
                [
                    html.P("Upload a CSV file with columns: Day, Steps, Calories.",
                           className="text-light"),
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(["📁 Drag and Drop or ", html.A("Select a CSV File")]),
                        style={
                            "width": "100%",
                            "height": "80px",
                            "lineHeight": "80px",
                            "borderWidth": "2px",
                            "borderStyle": "dashed",
                            "borderColor": "#ffeb3b",
                            "textAlign": "center",
                            "margin-bottom": "10px",
                        },
                        multiple=False,
                    ),
                    html.Div(id="upload-table"),
                ]
            ),
            className="shadow bg-dark border-warning",
        ),
    ],
    fluid=True,
)

# ===== About Page =====
about_layout = dbc.Container(
    [
        html.H2("ℹ️ About FitTrack", className="text-center text-warning my-4"),
        dbc.Card(
            dbc.CardBody(
                [
                    html.P(
                        "FitTrack is a Cloud Run app to visualize and analyze physical activity.",
                        className="text-light",
                    ),
                    html.P("Built with Dash + Bootstrap. Deployable as a Cloud Run service.",
                           className="text-secondary"),
                ]
            ),
            className="shadow bg-dark border-warning",
        ),
    ],
    fluid=True,
)

# ===== Master Layout =====
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        html.Div(id="page-content", className="p-3"),
    ]
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    if pathname == "/insights":
        return insights_layout
    elif pathname == "/upload":
        return upload_layout
    elif pathname == "/about":
        return about_layout
    else:
        return dashboard_layout(df)


# ===== Callback: advice section =====
@app.callback(Output("advice-output", "children"), Input("day-dropdown", "value"))
def advice_output(day):
    if not day:
        return ""
    row = df[df["Day"] == day].iloc[0]
    steps = int(row["Steps"])
    avg = int(df["Steps"].mean())
    diff = steps - avg
    if diff < -500:
        msg = "🚶 Less than average — go for a walk!"
        color = "danger"
    elif diff > 500:
        msg = "🔥 Above average — great job!"
        color = "warning"
    else:
        msg = "💪 Steady — great consistency."
        color = "success"

    return dbc.Alert([html.H5(day), html.P(msg)], color=color, className="mt-3")


# ===== Callback: Upload CSV =====
@app.callback(Output("upload-table", "children"), Input("upload-data", "contents"),
              State("upload-data", "filename"))
def upload_csv(contents, filename):
    if contents is None:
        return ""
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        new_df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    except Exception as e:
        return dbc.Alert(f"Error reading file: {e}", color="danger")

    # Validate columns
    required_cols = {"Day", "Steps", "Calories"}
    if not required_cols.issubset(new_df.columns):
        return dbc.Alert("Missing columns. Expected: Day, Steps, Calories", color="danger")

    # Display table
    return html.Div(
        [
            html.P(f"Uploaded file: {filename}", className="text-warning"),
            dash_table.DataTable(
                data=new_df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in new_df.columns],
                style_header={"backgroundColor": "#222", "color": "white"},
                style_cell={"backgroundColor": "#111", "color": "white"},
            ),
        ]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)