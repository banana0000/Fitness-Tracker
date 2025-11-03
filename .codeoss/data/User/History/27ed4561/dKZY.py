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

# Callback to update the enhanced Insights page
@callback(Output('insights-content', 'children'),
          Input('stored-data', 'data'))
def update_insights(jsonified_cleaned_data):
    if jsonified_cleaned_data is None:
        return dbc.Container([
            dbc.Card(dbc.CardBody(html.P("Please upload a CSV file on the Dashboard page to see your insights.", className="text-center")))
        ], fluid=True)

    df = pd.read_json(jsonified_cleaned_data, orient='split')
    if len(df) < 3:
        return dbc.Container([
            dbc.Card(dbc.CardBody(html.P("Upload at least 3 days of data for full insights.", className="text-center")))
        ], fluid=True)

    # --- 1. Calculate Core Metrics ---
    last_day = df.iloc[-1]
    previous_day = df.iloc[-2]
    avg_steps = df['Steps'].mean()
    avg_calories = df['Calories'].mean()
    best_steps_day = df.loc[df['Steps'].idxmax()]
    worst_steps_day = df.loc[df['Steps'].idxmin()]
    steps_diff_percent = ((last_day['Steps'] - previous_day['Steps']) / previous_day['Steps']) * 100 if previous_day['Steps'] > 0 else 0

    # --- 2. Build Insight Components ---
    insight_components = []

    # --- 2a. Actionable Smart Insight ---
    if steps_diff_percent > 5:
        recommendation_text = f"🔥 Fantastic work! You boosted your steps by {steps_diff_percent:.0f}% yesterday. Can you match that energy today and build a streak?"
        recommendation_color = "success"
    elif steps_diff_percent < -5:
        recommendation_text = f"😴 Your activity was a bit lower yesterday. Why not try a short 15-minute walk today to get back on track?"
        recommendation_color = "warning"
    else:
        recommendation_text = "💪 Great job staying consistent! To challenge yourself, try adding an extra 500 steps to your daily goal this week."
        recommendation_color = "info"

    smart_insight_card = dbc.Card(
        dbc.CardBody([
            html.H4("Your Smart Insight", className="card-title text-center"),
            html.Hr(),
            html.P(recommendation_text, className="card-text text-center fs-5"),
        ]), color=recommendation_color, inverse=True, className="mb-4"
    )
    insight_components.append(smart_insight_card)

    # --- 2b. Trend Analysis / Momentum Card ---
    trend_card = None
    if df.iloc[-1]['Steps'] > df.iloc[-2]['Steps'] and df.iloc[-2]['Steps'] > df.iloc[-3]['Steps']:
        trend_card = dbc.Card(
            dbc.CardBody([
                html.H5("📈 You're on a Roll!", className="card-title"),
                html.P("Your step count has increased for 3 days straight. Keep the momentum going!", className="card-text"),
            ]), color="success", outline=True, className="mb-4"
        )
    elif df.iloc[-1]['Steps'] < df.iloc[-2]['Steps'] and df.iloc[-2]['Steps'] < df.iloc[-3]['Steps']:
        trend_card = dbc.Card(
            dbc.CardBody([
                html.H5("📉 Let's Turn It Around", className="card-title"),
                html.P("Your activity has been trending down. Setting a small, achievable goal for today can help break the pattern.", className="card-text"),
            ]), color="danger", outline=True, className="mb-4"
        )
    if trend_card:
        insight_components.append(trend_card)

    # --- 2c. Main Grid of Cards ---
    main_grid_children = []

    # Weekly Snapshot Card
    summary_card = dbc.Card([
        dbc.CardHeader("Weekly Snapshot"),
        dbc.CardBody([
            html.H5("Average Daily Steps", className="card-title"),
            html.P(f"{avg_steps:,.0f}", className="fs-3 text-warning"),
            html.H5("Average Daily Calories Burned", className="card-title mt-3"),
            html.P(f"{avg_calories:,.0f}", className="fs-3 text-danger"),
        ])
    ], className="h-100")
    main_grid_children.append(dbc.Col(summary_card, md=6, className="mb-4"))

    # Correlation Insight Card
    high_activity_calories = df[df['Steps'] > avg_steps]['Calories'].mean()
    low_activity_calories = df[df['Steps'] <= avg_steps]['Calories'].mean()
    calorie_bonus = high_activity_calories - low_activity_calories if not pd.isna(high_activity_calories) and not pd.isna(low_activity_calories) else 0
    correlation_card = dbc.Card([
        dbc.CardHeader("The Power of Extra Steps"),
        dbc.CardBody([
            html.P("On your more active days (above average steps), you burned an average of:", className="card-text"),
            html.H4(f"{calorie_bonus:,.0f} extra calories!", className="text-success text-center"),
            html.P("Small changes make a big impact.", className="card-text text-muted text-center mt-2"),
        ])
    ], className="h-100")
    main_grid_children.append(dbc.Col(correlation_card, md=6, className="mb-4"))

    # Gamification / Trophy Room Card
    is_personal_best = last_day['Steps'] == df['Steps'].max()
    if is_personal_best and len(df) > 1:
        trophy_card = dbc.Card([
            dbc.CardHeader("🏆 New Personal Best!"),
            dbc.CardBody([
                html.P(f"You crushed it yesterday with {last_day['Steps']:,.0f} steps, setting a new record for this period! That's outstanding.", className="card-text"),
            ]),
        ], color="warning", inverse=True, className="h-100")
    else:
        trophy_card = dbc.Card([
            dbc.CardHeader("Trophy Room 🏆"),
            dbc.CardBody([
                html.P([html.Strong("Highest Step Count: "), f"{best_steps_day['Steps']:,.0f} on {best_steps_day['Day']}"], className="card-text"),
                html.Hr(),
                html.P([html.Strong("Lowest Step Count: "), f"{worst_steps_day['Steps']:,.0f} on {worst_steps_day['Day']}"], className="card-text text-muted"),
            ])
        ], className="h-100")
    main_grid_children.append(dbc.Col(trophy_card, md=6, className="mb-4"))

    # Progress Card
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
    main_grid_children.append(dbc.Col(progress_card, md=6, className="mb-4"))

    insight_components.append(dbc.Row(main_grid_children))

    return dbc.Container(insight_components, fluid=True)

if __name__ == '__main__':
    app.run(debug=True)