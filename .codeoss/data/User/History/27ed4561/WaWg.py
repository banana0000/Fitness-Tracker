from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

app = Dash(__name__)
server = app.server

# Load data
df = pd.read_csv("data.csv")
df["Day"] = pd.Categorical(
    df["Day"],
    categories=[
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"
    ],
    ordered=True,
)

avg_steps = int(df["Steps"].mean())
avg_cal = int(df["Calories"].mean())

# ==== DARK MODE CHART STYLES ====
fig_steps = px.line(
    df,
    x="Day",
    y="Steps",
    markers=True,
    title="Weekly Step Count",
    color_discrete_sequence=["#ffc107"],  # Yellow
)
fig_steps.update_traces(line=dict(width=3))
fig_steps.update_layout(
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ffeb3b"),  # bright yellow font
)

fig_calories = px.bar(
    df,
    x="Day",
    y="Calories",
    title="Calories Burned per Day",
    color_discrete_sequence=["#e53935"],  # Red
)
fig_calories.update_layout(
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ffcc00"),
)

# ==== LAYOUT ====
app.layout = html.Div(
    id="background",
    children=[
        html.Div(
            className="main-card",
            children=[
                html.H1("🏃 FitTrack Dark Mode", className="title"),
                html.P(
                    "Bold contrasts. High energy. Track your performance in style.",
                    className="subtitle",
                ),

                html.Div(
                    [
                        html.Div(
                            [html.H3("Average Steps"), html.H2(f"{avg_steps:,}")],
                            className="stat-block steps",
                        ),
                        html.Div(
                            [html.H3("Average Calories"), html.H2(f"{avg_cal:,}")],
                            className="stat-block calories",
                        ),
                    ],
                    className="stats-row",
                ),

                html.Div([dcc.Graph(figure=fig_steps, className="graph-card")]),
                html.Div([dcc.Graph(figure=fig_calories, className="graph-card")]),
                html.Hr(),

                # Interactive advice
                html.H3("Select a Day to Get Feedback", className="section-title"),
                dcc.Dropdown(
                    id="day-dropdown",
                    options=[{"label": d, "value": d} for d in df["Day"]],
                    value="Monday",
                    clearable=False,
                    className="dropdown",
                ),
                html.Div(id="advice-output", className="advice-box"),

                html.Footer(
                    "© 2025 FitTrack | Powered by Google Cloud Run 🚀",
                    className="footer",
                ),
            ],
        )
    ],
)

# Advice callback
@app.callback(Output("advice-output", "children"), [Input("day-dropdown", "value")])
def update_advice(selected_day):
    data = df[df["Day"] == selected_day]
    steps = int(data["Steps"].values[0])
    calories = int(data["Calories"].values[0])

    if steps < avg_steps * 0.8:
        msg = "You fell below your weekly average — time to ignite 🔥"
    elif steps > avg_steps * 1.1:
        msg = "Great job! You’re on fire! 🔥🔥"
    else:
        msg = "Solid consistency — keep the rhythm ⚡"

    return html.Div(
        [
            html.H4(selected_day, className="advice-title"),
            html.P(f"Steps: {steps:,} | Calories: {calories}", className="advice-data"),
            html.P(msg, className="advice-text"),
        ]
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)