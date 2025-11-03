import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px

app = Dash(__name__)
server = app.server

# CSV-ből adatbetöltés
df = pd.read_csv("data.csv")

fig_steps = px.line(df, x="Nap", y="Lépésszám", title="Heti lépésszám trend")
fig_calories = px.bar(df, x="Nap", y="Kalória", title="Heti kalóriaégetés")

app.layout = html.Div([
    html.H1("🏃♀️ FitTrack – Fizikai aktivitás dashboard"),
    dcc.Graph(figure=fig_steps),
    html.Br(),
    dcc.Graph(figure=fig_calories),
    html.Footer("Demo adatok CSV-ből – Valós integráció készül Google Fit API-val",
                style={"fontSize": "0.9em", "color": "#666"})
])

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080)
