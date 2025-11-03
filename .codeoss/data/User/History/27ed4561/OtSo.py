from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

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
        title="Estimated Calories Burned",
        color_discrete_sequence=["#e53935"],
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
    brand="🏃 FitTrack Smart",
    color="dark",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Add Steps", href="/add")),
    ],
)

# =========================================================
# Dashboard page
# =========================================================
def dashboard_page(data):
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
                                dbc.CardHeader("Average Calories (auto est.)"),
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


# =========================================================
# Add Data page (form)
# =========================================================
form_layout = dbc.Container(
    [
        html.H2("➕ Add Steps", className="text-center text-warning my-4"),
        dbc.Card(
            dbc.CardBody(
                [
                    html.P(
                        "Enter your daily steps. Calories will be calculated automatically.",
                        className="text-light",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(
                                    id="input-day",
                                    placeholder="Day (e.g. Monday)",
                                    type="text",
                                ),
                                md=6,
                            ),
                            dbc.Col(
                                dbc.Input(
                                    id="input-steps",
                                    placeholder="Steps",
                                    type="number",
                                ),
                                md=6,
                            ),
                        ],
                        className="mb-3",
                    ),
                    dbc.Button(
                        "Add Entry",
                        id="add-btn",
                        n_clicks=0,
                        color="warning",
                        className="text-dark mb-2",
                    ),
                    html.Div(id="add-status", className="text-success mb-3"),
                    dbc.Button(
                        "💾 Save to CSV",
                        id="save-btn",
                        color="danger",
                        className="text-light mb-4",
                        n_clicks=0,
                    ),
                    html.Div(id="save-status", className="text-info mb-4"),
                    dcc.Store(id="memory-data", data=df.to_dict("records")),
                    dcc.Graph(id="live-chart", config={"displayModeBar": False}),
                ]
            ),
            className="shadow bg-dark border-warning",
        ),
    ],
    fluid=True,
)

# =========================================================
# Layout and routing
# =========================================================
app.layout = html.Div(
    [dcc.Location(id="url"), navbar, html.Div(id="page-content", className="p-3")]
)


@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def routing(pathname):
    if pathname == "/add":
        return form_layout
    else:
        return dashboard_page(df)

# =========================================================
# Callbacks
# =========================================================

# --- Add new entry ---
@app.callback(
    [
        Output("memory-data", "data"),
        Output("add-status", "children"),
        Output("live-chart", "figure"),
    ],
    Input("add-btn", "n_clicks"),
    [
        State("input-day", "value"),
        State("input-steps", "value"),
        State("memory-data", "data"),
    ],
)
def add_entry(n_clicks, day, steps, current):
    if n_clicks == 0:
        fig_steps, _ = make_charts(pd.DataFrame(current))
        return current, "", fig_steps

    if not day or not steps:
        fig_steps, _ = make_charts(pd.DataFrame(current))
        return current, "⚠️ Please fill in both fields.", fig_steps

    df_local = pd.DataFrame(current)

    # auto-calc calories
    calories = int(int(steps) * 0.05)
    new_row = {"Day": day, "Steps": int(steps), "Calories": calories}

    # new pandas way: concat instead of append
    df_local = pd.concat([df_local, pd.DataFrame([new_row])], ignore_index=True)

    msg = f"✅ Added {day}: {steps} steps → {calories} kcal"
    fig_steps, _ = make_charts(df_local)
    return df_local.to_dict("records"), msg, fig_steps


# --- Save to CSV ---
@app.callback(
    Output("save-status", "children"),
    Input("save-btn", "n_clicks"),
    State("memory-data", "data"),
    prevent_initial_call=True,
)
def save_to_csv(n_clicks, data):
    if n_clicks > 0:
        df_save = pd.DataFrame(data)
        df_save.to_csv("data.csv", index=False)
        return f"✅ Data saved to data.csv ({len(df_save)} rows)"
    return ""


# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)