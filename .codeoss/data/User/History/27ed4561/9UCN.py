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
])

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

# Callback to store the uploaded data
@callback(Output('stored-data', 'data'),
          Output('dashboard-content', 'children'),
          Input('upload-data', 'contents'),
          State('upload-data', 'filename'))
def update_output(contents, filename):
    if contents is not None:
        df, error_message = parse_contents(contents, filename)
        if error_message:
            return None, html.Div([
                dbc.Alert(error_message, color="danger")
            ])
        if df is not None:
            dashboard_content = [
                dbc.Row([
                    dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='steps-chart'))), width=12),
                ]),
                html.Br(),
                dbc.Row([
                    dbc.Col(dbc.Card(dbc.CardBody(dcc.Graph(id='calories-chart'))), width=12),
                ])
            ]
            return df.to_json(date_format='iso', orient='split'), dashboard_content
    return None, html.Div([
        dbc.Card(
            dbc.CardBody(
                html.P("Please upload a CSV file to see your activity data.", className="text-center")
            )
        )
    ])

# Callback to update the steps chart
@callback(Output('steps-chart', 'figure'),
          Input('stored-data', 'data'))
def update_steps_chart(jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return {}
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    fig = px.line(df, x='Day', y='Steps', title='Daily Step Trends', template='plotly_dark')
    fig.update_traces(line=dict(color='yellow'))
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return fig

# Callback to update the calories chart
@callback(Output('calories-chart', 'figure'),
          Input('stored-data', 'data'))
def update_calories_chart(jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return {}
    df = pd.read_json(jsonified_cleaned_data, orient='split')
    fig = px.bar(df, x='Day', y='Calories', title='Daily Calories Burned', template='plotly_dark')
    fig.update_traces(marker_color='red')
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    return fig

# Callback to update the Insights page
@callback(Output('insights-content', 'children'),
          Input('stored-data', 'data'))
def update_insights(jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return dbc.Container([
            dbc.Card(
                dbc.CardBody(
                    html.P("Please upload a CSV file on the Dashboard page to see your insights.", className="text-center")
                )
            )
        ])

    df = pd.read_json(jsonified_cleaned_data, orient='split')

    if len(df) < 2:
        return dbc.Container([
            dbc.Card(
                dbc.CardBody(
                    html.P("You need at least two days of data to see insights.", className="text-center")
                )
            )
        ])

    last_day = df.iloc[-1]
    previous_day = df.iloc[-2]

    steps_diff = last_day['Steps'] - previous_day['Steps']
    calories_diff = last_day['Calories'] - previous_day['Calories']

    if steps_diff > 0:
        steps_recommendation = "🔥 You were more active yesterday!"
        steps_color = "success"
    elif steps_diff < 0:
        steps_recommendation = "😴 You slowed down yesterday — try moving more today!"
        steps_color = "warning"
    else:
        steps_recommendation = "💪 Consistent performance — great balance!"
        steps_color = "info"

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody([
                        html.H4("Daily Comparison", className="card-title"),
                        html.P(f"Steps yesterday: {last_day['Steps']} (Change: {steps_diff:+.0f})"),
                        html.P(f"Calories burned yesterday: {last_day['Calories']} (Change: {calories_diff:+.0f})"),
                    ]),
                color="dark",
                )
            ], width=12)
        ]),
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Card(
                    dbc.CardBody(
                        html.P(steps_recommendation, className="text-center")
                    ),
                color=steps_color,
                inverse=True
                )
            ], width=12)
        ])
    ])

if __name__ == '__main__':
    app.run(debug=True)