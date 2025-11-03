import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# --- Load Data ---
# Read the physical activity data from the CSV file
try:
    df = pd.read_csv('data.csv')
except FileNotFoundError:
    # Create a dummy dataframe for deployment environments where the file might not exist initially
    data = {'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            'Steps': [8500, 9200, 7800, 10500, 12300, 15200, 9500],
            'Calories': [350, 380, 320, 420, 500, 610, 390]}
    df = pd.DataFrame(data)


# --- Initialize the Dash App ---
app = dash.Dash(__name__)

# This line is crucial for Cloud Run deployment
server = app.server

# --- Create Figures ---
# 1. Line chart for Steps
fig_steps = px.line(
    df,
    x='Day',
    y='Steps',
    title='Daily Steps',
    markers=True,
    labels={'Steps': 'Number of Steps', 'Day': 'Day of the Week'}
)
fig_steps.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_color='#333',
    xaxis_gridcolor='#e0e0e0',
    yaxis_gridcolor='#e0e0e0'
)

# 2. Bar chart for Calories
fig_calories = px.bar(
    df,
    x='Day',
    y='Calories',
    title='Daily Calories Burned',
    labels={'Calories': 'Calories Burned', 'Day': 'Day of the Week'}
)
fig_calories.update_layout(
    plot_bgcolor='white',
    paper_bgcolor='white',
    font_color='#333',
    xaxis_gridcolor='#e0e0e0',
    yaxis_gridcolor='#e0e0e0'
)

# --- App Layout ---
app.layout = html.Div(style={'backgroundColor': '#f9f9f9', 'color': '#333', 'font-family': 'Arial, sans-serif', 'padding': '20px'}, children=[

    # Header
    html.H1(
        children='FitTrack - Weekly Activity Dashboard',
        style={'textAlign': 'center', 'color': '#1a73e8', 'marginBottom': '10px'}
    ),

    # Subtitle
    html.Div(
        children='Your weekly summary of steps taken and calories burned.',
        style={'textAlign': 'center', 'marginBottom': '30px', 'fontSize': '18px'}
    ),

    # First Graph: Steps
    dcc.Graph(
        id='steps-line-chart',
        figure=fig_steps
    ),

    # Separator
    html.Hr(style={'margin': '40px 0'}),

    # Second Graph: Calories
    dcc.Graph(
        id='calories-bar-chart',
        figure=fig_calories
    ),

    # Footer
    html.Footer(
        children='FitTrack Dashboard © 2025',
        style={'textAlign': 'center', 'marginTop': '40px', 'fontSize': '14px', 'color': '#777'}
    )
])

# --- Main entry point for running the app ---
if __name__ == '__main__':
    # The host='0.0.0.0' makes the app accessible from outside the container
    # The port=8080 is standard for many cloud services
    app.run_server(debug=False, host='0.0.0.0', port=8080)