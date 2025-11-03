from dash import Dash, html, dcc
import pandas as pd
import plotly.express as px

app = Dash(__name__)
server = app.server  # Fontos a Cloud Runhoz

# CSV beolvasása
df = pd.read_csv("data.csv")

# Grafikonok
fig_steps = px.line(df, x="Nap", y="Lépésszám", title="Heti Lépésszám Trend")
fig_calories = px.bar(df, x="Nap", y="Kalória", title="Heti Kalóriaégetés")

app.layout = html.Div(
    style={"fontFamily": "Arial", "margin": "40px"},
    children=[
        html.H1("🏃 FitTrack – Fizikai aktivitás dashboard"),
        html.P("Heti aktivitásaid vizualizálása Plotly Dash segítségével."),
        dcc.Graph(figure=fig_steps),
        html.Br(),
        dcc.Graph(figure=fig_calories),
        html.Footer(
            "Fejlesztette: Hackathon Team – Google Cloud Run-en üzemeltetve",
            style={"marginTop": "40px", "fontSize": "0.9em", "color": "#666"},
        ),
    ],
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=False)