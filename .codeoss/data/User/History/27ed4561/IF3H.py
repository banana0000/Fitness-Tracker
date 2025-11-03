import base64
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc

# Initialize the Dash app with the Darkly theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], suppress_callback_exceptions=True)
server = app.server

# Define the navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Dashboard", href="/")),
        dbc.NavItem(dbc.NavLink("Insights", href="/insights")),
    ],
    brand="Physical Activity Tracker",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4",
)

# Define the layout for the Dashboard page
dashboard_layout = dbc.Container([
    dcc.Store(id='stored-data'),
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4("Upload Your Activity Data", className="card-title"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A('Select a CSV File')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                        },
                    ),
                ])
            )
        ], width=12)
    ]),
    html.Br(),
    html.Div(id='dashboard-content')
], fluid=True)

# Define the layout for the Insights page
insights_layout = html.Div(id='insights-content')

# Main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content')
])

# Callback to render the correct page based on the URL
@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/insights':
        return insights_layout
    else:
        return dashboard_layout

# Function to parse the uploaded CSV file
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            # Basic validation for required columns
            if not {'Day', 'Steps', 'Calories'}.issubset(df.columns):
                return None, "Error: CSV must contain 'Day', 'Steps', and 'Calories' columns."
            return df, None
        else:
            return None, "Error: Please upload a CSV file."
    except Exception as e:
        print(e)
        return None, "There was an error processing this file."

# Callback to store the uploaded data and update dashboard
@callback(Output('stored-data', 'data'),
          Output('dashboard-content', 'children'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename'))
def update_output(contents, filename):
    if contents is not None:
        df, error_message = parse_contents(contents, filename)
        if error_message:
            return None, html.Div([dbc.Alert(error_message, color="danger")])
        if df is not None:
            dashboard_content = [
                dbc.Row([
                    dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='steps-chart'))), width=12, className="mb-4"),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='calories-chart'))), width=12),
                ])
            ]
            return df.to_json(date_format='iso', orient='split'), dashboard_content
    return None, dbc.Card(dbc.CardBody(html.P("Please upload a CSV file to see your activity data.", className="text-center")))

# Callback to update the steps chart
@callback(Output('steps-chart', 'figure'),
          Input('stored-data', 'data'))
def update_steps_chart(jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return go.Figure().update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    fig = px.line(df, x='Day', y='Steps', title='Daily Step Trends', template='plotly_dark', markers=True)
    fig.update_traces(line=dict(color='yellow'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

# Callback to update the calories chart
@callback(Output('calories-chart', 'figure'),
          Input('stored-data', 'data'))
def update_calories_chart(jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return go.Figure().update_layout(template='plotly_dark', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    fig = px.bar(df, x='Day', y='Calories', title='Daily Calories Burned', template='plotly_dark')
    fig.update_traces(marker_color='red')
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    return fig

# Callback to update the new, more interesting Insights page
@callback(Output('insights-content', 'children'),
          Input('stored-data', 'data'))
def update_insights(jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return dbc.Container([
            dbc.Card(dbc.CardBody(html.P("Please upload a CSV file on the Dashboard page to see your insights.", className="text-center")))
        ], fluid=True)

    df = pd.read_json(jsonified_cleaned_data, orient='split')
    if len(df) < 2:
        return dbc.Container([
            dbc.Card(dbc.CardBody(html.P("You need at least two days of data for meaningful insights.", className="text-center")))
        ], fluid=True)

    # --- Calculate Metrics ---
    avg_steps = df['Steps'].mean()
    avg_calories = df['Calories'].mean()
    best_steps_day = df.loc[df['Steps'].idxmax()]
    worst_steps_day = df.loc[df['Steps'].idxmin()]
    last_day = df.iloc[-1]
    previous_day = df.iloc[-2]
    steps_diff = last_day['Steps'] - previous_day['Steps']
    steps_diff_percent = (steps_diff / previous_day['Steps']) * 100 if previous_day['Steps'] != 0 else 0

    # --- Smart Recommendation Logic ---
    if steps_diff_percent > 5:
        recommendation_text = f"🔥 Great job! Your step count increased by {steps_diff_percent:.0f}% yesterday."
        recommendation_color = "success"
    elif steps_diff_percent < -5:
        recommendation_text = f"😴 It looks like you slowed down yesterday. A great day to get back on track!"
        recommendation_color = "warning"
    else:
        recommendation_text = "💪 Consistent performance — you're building a great habit!"
        recommendation_color = "info"

    # --- Build Layout Components ---
    recommendation_card = dbc.Card(
        dbc.CardBody([
            html.H4("Your Smart Insight", className="card-title text-center"),
            html.Hr(),
            html.P(recommendation_text, className="card-text text-center fs-5"),
        ]),
        color=recommendation_color,
        inverse=True,
        className="mb-4"
    )

    summary_card = dbc.Card([
        dbc.CardHeader("Weekly Snapshot"),
        dbc.CardBody([
            html.H5("Average Daily Steps", className="card-title"),
            html.P(f"{avg_steps:,.0f}", className="fs-3 text-warning"),
            html.H5("Average Daily Calories Burned", className="card-title mt-3"),
            html.P(f"{avg_calories:,.0f}", className="fs-3 text-danger"),
        ])
    ], className="h-100")

    progress_card = dbc.Card([
        dbc.CardHeader("Yesterday vs. Your Average"),
        dbc.CardBody([
            html.Div([
                html.P("Steps Progress"),
                dbc.Progress(value=(last_day['Steps'] / avg_steps) * 100, label=f"{(last_day['Steps'] / avg_steps) * 100:.0f}%", color="warning", style={"height": "20px"}),
                html.Small(f"{last_day['Steps']:,.0f} of {avg_steps:,.0f} avg steps", className="text-muted"),
            ], className="mb-3"),
            html.Div([
                html.P("Calories Progress"),
                dbc.Progress(value=(last_day['Calories'] / avg_calories) * 100, label=f"{(last_day['Calories'] / avg_calories) * 100:.0f}%", color="danger", style={"height": "20px"}),
                html.Small(f"{last_day['Calories']:,.0f} of {avg_calories:,.0f} avg calories", className="text-muted"),
            ]),
        ])
    ], className="h-100")

    trophy_card = dbc.Card([
        dbc.CardHeader("Trophy Room 🏆"),
        dbc.CardBody([
            html.P([html.Strong("Highest Step Count: "), f"{best_steps_day['Steps']:,.0f} on {best_steps_day['Day']}"], className="card-text"),
            html.P([html.Strong("Lowest Step Count: "), f"{worst_steps_day['Steps']:,.0f} on {worst_steps_day['Day']}"], className="card-text text-muted"),
        ])
    ])

    return dbc.Container([
        recommendation_card,
        dbc.Row([
            dbc.Col(summary_card, md=6, lg=4, className="mb-4"),
            dbc.Col(progress_card, md=6, lg=4, className="mb-4"),
            dbc.Col(trophy_card, md=12, lg=4, className="mb-4"),
        ]),
    ], fluid=True)

if __name__ == '__main__':
    app.run(debug=True)