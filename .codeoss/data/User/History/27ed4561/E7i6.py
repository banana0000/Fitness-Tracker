from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

app = Dash(__name__)
server = app.server

# Data
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

# Charts
fig_steps = px.line(
    df,
    x="Day",
    y="Steps",
    markers=True,
    title="Weekly Step Count",
    color_discrete_sequence=["#1565c0"],
)
fig_steps.update_layout(
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
)
fig_calories = px.bar(
    df,
    x="Day",
    y="Calories",
    title="Calories Burned per Day",
    color_discrete_sequence=["#2e7d32"],
)
fig_calories.update_layout(
    title_x=0.5,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
)

# Layout
app.layout = html.Div(
    id="background",
    children=[
        html.Div(
            className="main-card",
            children=[
                html.H1("🏃 FitTrack", className="title"),
                html.P(
                    "Your weekly health dashboard — visualize, track and get advice.",
                    className="subtitle",
                ),

                html.Div(
                    [
                        html.Div(
                            [html.H3("Avg Steps"), html.H2(f"{avg_steps:,} 👣")],
                            className="stat-block",
                        ),
                        html.Div(
                            [html.H3("Avg Calories"), html.H2(f"{avg_cal:,} kcal 🔥")],
                            className="stat-block",
                        ),
                    ],
                    className="stats-row",
                ),
                html.Div([dcc.Graph(figure=fig_steps, className="graph-card")]),
                html.Div([dcc.Graph(figure=fig_calories, className="graph-card")]),
                html.Hr(),
                html.Div(
                    [
                        html.H3("🔍 Choose a Day", className="section-title"),
                        dcc.Dropdown(
                            id="day-dropdown",
                            options=[{"label": d, "value": d} for d in df["Day"]],
                            value="Monday",
                            clearable=False,
                            className="dropdown",
                        ),
                        html.Div(id="advice-output", className="advice-box"),
                    ]
                ),
                html.Footer(
                    "Developed for Google Cloud Run Hackathon 2025 🚀",
                    className="footer",
                ),
            ],
        )
    ],
)

# Callback for advice
@app.callback(Output("advice-output", "children"), [Input("day-dropdown", "value")])
def update_advice(selected_day):
    data = df[df["Day"] == selected_day]
    steps = int(data["Steps"].values[0])
    calories = int(data["Calories"].values[0])

    if steps < avg_steps * 0.8:
        advice = "Walk a bit more tomorrow! Try short breaks and evening walks."
    elif steps > avg_steps * 1.1:
        advice = "You're crushing it! Keep up the great momentum!"
    else:
        advice = "You're on track — consistency is key."

    return html.Div(
        [
            html.H4(f"{selected_day}", className="advice-title"),
            html.P(f"Steps: {steps:,} | Calories: {calories}", className="advice-data"),
            html.P(advice, className="advice-text"),
        ]
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)