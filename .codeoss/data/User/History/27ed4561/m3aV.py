from dash import Dash, html, dcc
import pandas as pd
import plotly.express as px

app = Dash(__name__)
server = app.server  # Required for Cloud Run

# 1️⃣ Load physical activity data
df = pd.read_csv("data.csv")

# 2️⃣ Compute key statistics
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

# 3️⃣ Create interactive charts with Plotly
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

# 4️⃣ Layout — clean, centered, organized layout
app.layout = html.Div(
    className="main-container",
    children=[
        html.H1("🏃 FitTrack – Physical Activity Dashboard", className="title"),
        html.P(
            "Visualize your weekly activity trends in a clean, serverless dashboard built with Dash and Cloud Run."
        ),
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
                        html.H3("Average Calories Burned"),
                        html.H2(f"{avg_cal:,} kcal/day".replace(",", " ")),
                    ],
                    className="stat-box calories",
                ),
            ],
            className="stats-row",
        ),
        html.Div([dcc.Graph(figure=fig_steps)], className="graph-box"),
        html.Div([dcc.Graph(figure=fig_calories)], className="graph-box"),
        html.Footer(
            "Developed by the Hackathon Team | Powered by Google Cloud Run 🚀",
            className="footer",
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)