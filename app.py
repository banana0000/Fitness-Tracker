import base64
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State, callback # <-- FIXED THIS LINE
import dash_bootstrap_components as dbc

# Initialize the Dash app with the Darkly theme
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Define a reusable function for creating summary cards
def create_summary_card(title, value, color):
    return dbc.Card(
        dbc.CardBody([
            html.P(title, className="card-title text-muted"),
            html.H3(value, className=f"card-text text-{color}"),
        ]),
        className="text-center"
    )

# --- App Layout ---
app.layout = dbc.Container([
    # Store component to hold the DataFrame JSON
    dcc.Store(id='stored-data'),

    # Header and Title
    dbc.Row(
        dbc.Col(
            html.H1("Physical Activity Dashboard", className="text-center my-4"),
            width=12
        )
    ),

    # File Upload Component
    dbc.Row(
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Upload Your Activity Data", className="card-title"),
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div(['Drag and Drop or ', html.A('Select a CSV File')]),
                        style={
                            'width': '100%', 'height': '60px', 'lineHeight': '60px',
                            'borderWidth': '1px', 'borderStyle': 'dashed',
                            'borderRadius': '5px', 'textAlign': 'center',
                        },
                    ),
                ])
            ),
            width=12
        ),
        className="mb-4"
    ),

    # This Div will be populated with content after a file is uploaded
    html.Div(id='output-content'),

], fluid=True)


# --- Callbacks ---

# Callback to parse the uploaded file and store the data
@callback(
    Output('stored-data', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def parse_and_store_data(contents, filename):
    if contents is None:
        return None  # No file uploaded yet

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            # Validate required columns
            if not {'Day', 'Steps', 'Calories'}.issubset(df.columns):
                # In a real app, you might return an error message to an alert component
                print("Error: CSV must contain 'Day', 'Steps', and 'Calories' columns.")
                return None
            return df.to_json(date_format='iso', orient='split')
        else:
            print("Error: Please upload a CSV file.")
            return None
    except Exception as e:
        print(f"File processing error: {e}")
        return None

# Callback to generate the entire output page (summary and charts) from the stored data
@callback(
    Output('output-content', 'children'),
    Input('stored-data', 'data')
)
def update_output_content(jsonified_cleaned_data):
    # If no data is stored, show the empty state message
    if jsonified_cleaned_data is None:
        return dbc.Card(
            dbc.CardBody(
                html.P("Please upload a CSV file to see your activity dashboard.", className="text-center text-muted")
            )
        )

    # If data is available, generate the dashboard
    df = pd.read_json(jsonified_cleaned_data, orient='split')

    # --- 1. Calculate Summary Metrics ---
    total_steps = df['Steps'].sum()
    avg_steps = df['Steps'].mean()
    total_calories = df['Calories'].sum()
    best_day_data = df.loc[df['Steps'].idxmax()]
    best_day_text = f"{best_day_data['Day']} ({best_day_data['Steps']:,} steps)"

    # --- 2. Create Figures for Charts ---
    # Steps Line Chart
    steps_fig = px.line(df, x='Day', y='Steps', title='Daily Step Trends', template='plotly_dark', markers=True)
    steps_fig.update_traces(line=dict(color='yellow'))
    steps_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

    # Calories Bar Chart
    calories_fig = px.bar(df, x='Day', y='Calories', title='Daily Calories Burned', template='plotly_dark')
    calories_fig.update_traces(marker_color='red')
    calories_fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')

    # --- 3. Assemble the Layout ---
    summary_and_charts_layout = html.Div([
        # Summary Row
        dbc.Row([
            dbc.Col(create_summary_card("Total Steps", f"{total_steps:,}", "light"), md=3, className="mb-2"),
            dbc.Col(create_summary_card("Average Daily Steps", f"{avg_steps:,.0f}", "light"), md=3, className="mb-2"),
            dbc.Col(create_summary_card("Total Calories Burned", f"{total_calories:,}", "light"), md=3, className="mb-2"),
            dbc.Col(create_summary_card("Best Day for Steps", best_day_text, "warning"), md=3, className="mb-2"),
        ], className="mb-4"),

        # Charts Row
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=steps_fig)), md=6, className="mb-4 mb-md-0"),
            dbc.Col(dbc.Card(dcc.Graph(figure=calories_fig)), md=6),
        ]),
    ])

    return summary_and_charts_layout


if __name__ == '__main__':
    app.run(debug=True)