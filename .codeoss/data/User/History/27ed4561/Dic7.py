from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# ===== App setup =====
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# ===== Load data =====
df = pd.read_csv("data.csv")
df["Day"] = pd.Categorical(
    df["Day"],
    categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    ordered=True,
)

avg_steps = int(df["Steps"].mean())
avg_cal = int(df["Calories"].mean())

# ===== Charts =====
fig_steps = px.line(
    df,
    x="Day",
    y="Steps",
    markers=True,
    title="Weekly Step Count",
    color_discrete_sequence=["#ffeb3b"],  # Yellow
)
fig_steps.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#fff"),
    title_x=0.5,
)

fig_calories = px.bar(
    df,
    x="Day",
    y="Calories",
    title="Calories Burned per Day",
    color_discrete_sequence=["#e53935"],  # Red
)
fig_calories.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#fff"),
    title_x=0.5,
)

# ===== Navbar =====
navbar = dbc.NavbarSimple(
    brand="🏃 FitTrack Dark",
    color="dark",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Insights", href="/insights")),
        dbc.NavItem(dbc.NavLink("About", href="/about")),
    ],
)

# ===== Page 1: Dashboard =====
dashboard_layout = dbc.Container(
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
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Steps Overview"),
                            dbc.CardBody(dcc.Graph(figure=fig_steps)),
                        ],
                        className="shadow bg-dark border-warning",
                    ),
                    md=6,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Calories Overview"),
                            dbc.CardBody(dcc.Graph(figure=fig_calories)),
                        ],
                        className="shadow bg-dark border-danger",
                    ),
                    md=6,
                ),
            ],
            className="gy-3",
        ),
    ],
    fluid=True,
)

# ===== Page 2: Insights =====
insights_layout = dbc.Container(
    [
        html.H2("💬 Insights", className="text-center text-warning my-4"),
        dbc.Card(
            [
                dbc.CardBody(
                    [
                        html.P("Select a day to get personalized fitness advice below:",
                               className="lead text-white"),
                        dcc.Dropdown(
                            id="day-dropdown",
                            options=[{"label": d, "value": d} for d in df["Day"]],
                            value="Monday",
                            className="mb-4",
                            clearable=False,
                            style={"color": "#000"},
                        ),
                        html.Div(id="advice-output"),
                    ]
                )
            ],
            className="shadow bg-dark border-warning",
        ),
    ],
    fluid=True,
)

# ===== Page 3: About =====
about_layout = dbc.Container(
    [
        html.H2("ℹ️ About FitTrack", className="text-center text-warning my-4"),
        dbc.Card(
            dbc.CardBody(
                [
                    html.P(
                        "FitTrack is a serverless fitness analytics dashboard built with Python, Plotly Dash, and Dash Bootstrap Components.",
                        className="text-light",
                    ),
                    html.P(
                        "Deployed on Google Cloud Run for the 2025 Cloud Run Hackathon. "
                        " Integrates data, interactivity, and AI-style insights.",
                        className="text-secondary",
                    ),
                    html.P(
                        "Created with 🖤 by Hackathon Team | #CloudRunHackathon",
                        className="text-danger fw-bold",
                    ),
                ]
            ),
            className="shadow bg-dark border-warning",
        ),
    ],
    fluid=True,
)

# ===== Routing (dcc.Location + callback) =====
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        html.Div(id="page-content", className="p-3"),
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page(path):
    if path == "/insights":
        return insights_layout
    elif path == "/about":
        return about_layout
    else:
        return dashboard_layout


# ===== Advice logic =====
@app.callback(Output("advice-output", "children"), [Input("day-dropdown", "value")])
def generate_advice(day):
    if not day:
        return ""

    row = df[df["Day"] == day].iloc[0]
    steps = int(row["Steps"])
    diff = steps - avg_steps

    if diff < -500:
        msg = "🚶♂️ You walked less than your weekly average — a short evening walk would help!"
        color = "danger"
    elif diff > 500:
        msg = "🔥 Amazing! You beat your weekly average!"
        color = "warning"
    else:
        msg = "💪 Steady and consistent! Keep up the balance."
        color = "success"

    return dbc.Card(
        dbc.CardBody(
            [
                html.H5(f"{day}", className=f"text-{color}"),
                html.P(f"Steps: {steps:,}", className="mb-1"),
                html.P(msg, className=f"text-{color} fw-bold"),
            ]
        ),
        className=f"mt-3 bg-dark border-{color} shadow",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)