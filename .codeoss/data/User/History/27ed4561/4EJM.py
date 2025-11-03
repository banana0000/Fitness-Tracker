from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

# ===== Basic setup =====
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# ===== Data =====
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
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ffeb3b"),
)

fig_cal = px.bar(
    df,
    x="Day",
    y="Calories",
    title="Calories Burned Each Day",
    color_discrete_sequence=["#e53935"],  # Red
)
fig_cal.update_layout(
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e53935"),
)

# ===== Navbar (top) =====
navbar = html.Nav(
    className="navbar",
    children=[
        html.Div("🏃♂️ FitTrack Pro", className="nav-logo"),
        html.Div(
            [
                dcc.Link("Dashboard", href="/", className="nav-link"),
                dcc.Link("Insights", href="/insights", className="nav-link"),
                dcc.Link("About", href="/about", className="nav-link"),
            ],
            className="nav-links",
        ),
    ],
)

# ===== Page layouts =====
dashboard_layout = html.Div(
    className="page",
    children=[
        html.H1("Dashboard", className="page-title"),
        html.Div(
            [
                dcc.Graph(figure=fig_steps, className="graph-card"),
                dcc.Graph(figure=fig_cal, className="graph-card"),
            ],
        ),
    ],
)

insights_layout = html.Div(
    className="page",
    children=[
        html.H1("Insights", className="page-title"),
        html.P("Select a day to get personalized activity advice 💡", className="page-text"),
        dcc.Dropdown(
            id="day-dropdown",
            options=[{"label": d, "value": d} for d in df["Day"]],
            value="Monday",
            className="dropdown",
            clearable=False,
        ),
        html.Div(id="advice-box", className="advice-box"),
    ],
)

about_layout = html.Div(
    className="page",
    children=[
        html.H1("About FitTrack", className="page-title"),
        html.P("Built for the Google Cloud Run Hackathon 2025.", className="page-text"),
        html.P(
            "FitTrack is a fitness analytics dashboard that helps visualize weekly activity data, "
            "deployed entirely on Google Cloud Run as a serverless Dash application.",
            className="page-text",
        ),
        html.P(
            "Created with ❤️ & Python by Hackathon Team.\n\n#CloudRunHackathon",
            className="page-text",
        ),
    ],
)

# ===== App layout (main) =====
app.layout = html.Div(
    [
        dcc.Location(id="url"),
        navbar,
        html.Div(id="page-content", className="content-container"),
    ]
)

# ===== Routing logic =====
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/insights":
        return insights_layout
    elif pathname == "/about":
        return about_layout
    else:
        return dashboard_layout


# ===== Advice callback =====
@app.callback(Output("advice-box", "children"), [Input("day-dropdown", "value")])
def update_advice(selected_day):
    if not selected_day:
        return ""

    row = df[df["Day"] == selected_day]
    steps = int(row["Steps"].iloc[0])
    calories = int(row["Calories"].iloc[0])
    avg = avg_steps

    if steps < avg * 0.8:
        msg = "⚠ You walked less than your average — get moving!"
    elif steps > avg * 1.2:
        msg = "🔥 Excellent! You're above your weekly average!"
    else:
        msg = "💪 You're right around your average. Keep it steady!"

    return html.Div(
        [
            html.H4(f"{selected_day}", className="advice-title"),
            html.P(f"Steps: {steps:,} | Calories: {calories}", className="advice-data"),
            html.P(msg, className="advice-text"),
        ]
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)