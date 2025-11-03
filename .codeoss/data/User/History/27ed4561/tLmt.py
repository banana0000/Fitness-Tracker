from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# ===== App setup =====
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
server = app.server

# ===== Default dataset =====
df = pd.read_csv("data.csv")
df["Day"] = pd.Categorical(
    df["Day"],
    categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    ordered=True,
)

# ===== Helper: create chart based on dataframe =====
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
        title_x=0.5,
        font=dict(color="#fff"),
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
        title_x=0.5,
        font=dict(color="#fff"),
    )
    return fig_steps, fig_cal


# ===== Navbar =====
navbar = dbc.NavbarSimple(
    brand="🏃 FitTrack Form",
    color="dark",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Add Data", href="/add")),
    ],
)

# ===== Dashboard layout =====
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
                                dbc.CardHeader("Average Steps", className="text-warning"),
                                dbc.CardBody(
                                    html.H4(f"{avg_steps:,}", className="text-warning text-center")
                                ),
                            ],
                            className="shadow bg-dark border-warning",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader("Average Calories", className="text-danger"),
                                dbc.CardBody(
                                    html.H4(f"{avg_cal:,} kcal", className="text-danger text-center")
                                ),
                            ],
                            className="shadow bg-dark border-danger",
                        ),
                        md=6,
                    ),
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [dbc.CardBody(dcc.Graph(figure=fig_steps))],
                            className="shadow bg-dark border-warning",
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Card(
                            [dbc.CardBody(dcc.Graph(figure=fig_cal))],
                            className="shadow bg-dark border-danger",
                        ),
                        md=6,
                    ),
                ]
            ),
        ],
        fluid=True,
    )


# ===== Add Data (Form layout) =====
form_layout = dbc.Container(
    [
        html.H2("➕ Add Activity Data", className="text-center text-warning my-4"),
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.P("Enter your daily activity below:", className="text-light"),
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Input(
                                        id="input-day",
                                        placeholder="Day (e.g. Monday)",
                                        type="text",
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    dbc.Input(
                                        id="input-steps",
                                        placeholder="Steps",
                                        type="number",
                                    ),
                                    md=4,
                                ),
                                dbc.Col(
                                    dbc.Input(
                                        id="input-calories",
                                        placeholder="Calories",
                                        type="number",
                                    ),
                                    md=4,
                                ),
                            ],
                            className="mb-3",
                        ),
                        dbc.Button(
                            "Add Entry",
                            id="btn-add",
                            color="warning",
                            className="mb-3 text-dark",
                            n_clicks=0,
                        ),
                        html.Div(id="add-status", className="text-success mb-4"),
                        dcc.Store(id="memory-data", data=df.to_dict("records")),
                        dbc.Card(
                            dbc.CardBody(
                                dcc.Graph(id="chart-preview", config={"displayModeBar": False})
                            ),
                            className="shadow bg-dark border-warning",
                        ),
                    ]
                )
            ],
            className="shadow bg-dark border-warning",
        ),
    ],
    fluid=True,
)


# ===== Main app layout =====
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        html.Div(id="page-content", className="p-3"),
    ]
)


# ===== Routing =====
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page(path):
    if path == "/add":
        return form_layout
    else:
        return dashboard_layout(df)


# ===== Callback: form logic =====
@app.callback(
    [Output("memory-data", "data"), Output("add-status", "children"), Output("chart-preview", "figure")],
    Input("btn-add", "n_clicks"),
    [State("input-day", "value"), State("input-steps", "value"), State("input-calories", "value"),
     State("memory-data", "data")],
)
def update_data(n_clicks, day, steps, cal, current):
    if n_clicks == 0:
        fig_steps, _ = make_charts(pd.DataFrame(current))
        return current, "", fig_steps

    if not day or not steps or not cal:
        fig_steps, _ = make_charts(pd.DataFrame(current))
        return current, "⚠️ Please fill all fields.", fig_steps

    df_local = pd.DataFrame(current)
    # Append new record
    new = {"Day": day, "Steps": int(steps), "Calories": int(cal)}
    df_local = df_local.append(new, ignore_index=True)

    message = f"✅ Added {day}: {steps} steps, {cal} cal"
    fig_steps, _ = make_charts(df_local)
    return df_local.to_dict("records"), message, fig_steps


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)