from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# =========================================================
# Setup
# =========================================================
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# =========================================================
# Load dataset
# =========================================================
df = pd.read_csv("data.csv")
df["Day"] = pd.Categorical(
    df["Day"],
    categories=["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"],
    ordered=True,
)

avg_steps = int(df["Steps"].mean())
avg_cal = int(df["Calories"].mean())

# =========================================================
# Helper charts
# =========================================================
def make_charts(data):
    fig_steps = px.line(
        data, x="Day", y="Steps", markers=True,
        title="Weekly Step Count Trend",
        color_discrete_sequence=["#ffeb3b"]
    )
    fig_steps.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_x=0.5, font=dict(color="#fff")
    )
    fig_cal = px.bar(
        data, x="Day", y="Calories",
        title="Weekly Calories Burned",
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
        dbc.NavItem(dbc.NavLink("Insights", href="/insights")),
    ],
)

# =========================================================
# Dashboard layout
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
                                dbc.CardHeader("Average Calories Burned"),
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
# Insights page
# =========================================================

# determine last two days for comparison
yesterday = df.iloc[-1]
previous_day = df.iloc[-2]

def create_insight_card():
    diff_steps = yesterday["Steps"] - previous_day["Steps"]
    diff_cal = yesterday["Calories"] - previous_day["Calories"]

    if diff_steps > 500:
        msg = "🔥 You were more active than the previous day. Keep that momentum!"
        color = "success"
    elif diff_steps < -500:
        msg = "😴 A slower day yesterday — try to move a bit more today!"
        color = "danger"
    else:
        msg = "💪 Consistent performance — steady progress!"
        color = "warning"

    card = dbc.Card(
        dbc.CardBody(
            [
                html.H4("📅 Yesterday Summary", className="text-warning mb-3"),
                html.P(f"Day: {yesterday['Day']}", className="text-light mb-1"),
                html.P(f"Steps: {int(yesterday['Steps']):,}"
                       f" ({'+' if diff_steps>0 else ''}{diff_steps})",
                       className="text-light mb-1"),
                html.P(f"Calories: {int(yesterday['Calories']):,}"
                       f" ({'+' if diff_cal>0 else ''}{diff_cal}) kcal",
                       className="text-light mb-3"),
                html.Div(msg, className=f"alert alert-{color} mt-2 mb-0"),
            ]
        ),
        className="shadow bg-dark border-warning",
    )
    return card


def insights_page():
    return dbc.Container(
        [
            html.H2("💬 Daily Insights", className="text-center text-warning my-4"),
            html.P("Smart activity recommendations based on your latest data.",
                   className="text-center text-light mb-4"),
            create_insight_card(),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H5("Trend Overview", className="text-warning"),
                        dcc.Graph(figure=make_charts(df)[0],
                                  config={'displayModeBar': False}),
                    ]
                ),
                className="shadow bg-dark border-warning mt-4",
            ),
        ],
        fluid=True,
    )

# =========================================================
# App layout & routing
# =========================================================
app.layout = html.Div(
    [dcc.Location(id="url"),
     navbar,
     html.Div(id="page-content", className="p-3")]
)

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def routing(pathname):
    if pathname == "/insights":
        return insights_page()
    else:
        return dashboard_page(df)

# =========================================================
# Run app
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)