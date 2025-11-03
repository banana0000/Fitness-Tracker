from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

app = Dash(__name__)
server = app.server

# Load CSV data
df = pd.read_csv("data.csv")

# Ensure day order
df["Day"] = pd.Categorical(
    df["Day"],
    categories=[
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ],
    ordered=True,
)

avg_steps = int(df["Steps"].mean())
avg_cal = int(df["Calories"].mean())

# Graphs
fig_steps = px.line(
    df,
    x="Day",
    y="Steps",
    markers=True,
    title="Weekly Step Count Trend",
    color_discrete_sequence=["#1976d2"],
)
fig_steps.update_traces(line=dict(width=4))
fig_steps.update_layout(plot_bgcolor="#fafafa", paper_bgcolor="#fafafa")

fig_calories = px.bar(
    df,
    x="Day",
    y="Calories",
    title="Weekly Calories Burned",
    color_discrete_sequence=["#43a047"],
)
fig_calories.update_layout(plot_bgcolor="#fafafa", paper_bgcolor="#fafafa")

# Layout
app.layout = html.Div(
    className="main-container",
    children=[
        html.H1("🏃 FitTrack – Physical Activity Dashboard", className="title"),
        html.P(
            "Analyze your weekly activity and get smart wellness advice powered by AI-style logic."
        ),

        # Overall statistics
        html.Div(
            [
                html.Div(
                    [
                        html.H3("Average Steps"),
                        html.H2(f"{avg_steps:,} steps/week".replace(",", " ")),
                    ],
                    className="stat-box steps",
                ),
                html.Div(
                    [
                        html.H3("Average Calories"),
                        html.H2(f"{avg_cal:,} kcal/day".replace(",", " ")),
                    ],
                    className="stat-box calories",
                ),
            ],
            className="stats-row",
        ),

        html.Div([dcc.Graph(figure=fig_steps)], className="graph-box"),
        html.Div([dcc.Graph(figure=fig_calories)], className="graph-box"),
        html.Hr(),

        # Interactive query section
        html.Div(
            [
                html.H3("🔍 Choose a day to get personalized feedback:", className="section-title"),
                dcc.Dropdown(
                    id="day-dropdown",
                    options=[{"label": d, "value": d} for d in df["Day"]],
                    value="Monday",
                    clearable=False,
                    className="dropdown"
                ),
                html.Div(id="advice-output", className="advice-box"),
            ],
            className="query-section",
        ),

        html.Footer(
            "Developed by Hackathon Team – Powered by Google Cloud Run 🚀",
            className="footer",
        ),
    ],
)

# Callback for advice generator
@app.callback(Output("advice-output", "children"), [Input("day-dropdown", "value")])
def update_advice(selected_day):
    data = df[df["Day"] == selected_day]
    steps = int(data["Steps"].values[0])
    calories = int(data["Calories"].values[0])

    # Simple AI-style logic
    if steps < avg_steps * 0.8:
        advice = "You walked less than your weekly average. Try a short evening walk or take the stairs more often 🏃♂️."
    elif steps > avg_steps * 1.1:
        advice = "Excellent! You are above your average — keep it up 🔥."
    else:
        advice = "You're right around your weekly average. Maintain consistency and stay active 💪."

    return html.Div(
        [
            html.H4(f"{selected_day} Summary", className="advice-title"),
            html.P(f"Lépésszám: {steps:,} | Calories burned: {calories}", className="advice-data"),
            html.P(advice, className="advice-text"),
        ],
    )

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)