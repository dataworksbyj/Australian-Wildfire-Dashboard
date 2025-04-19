import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update

# Load the data
wildfire_df = pd.read_csv('../data/wildfire_data.csv')

# Extract time features
wildfire_df['Date'] = pd.to_datetime(wildfire_df['Date'])
wildfire_df['Month'] = wildfire_df['Date'].dt.strftime('%B')
wildfire_df['Year'] = wildfire_df['Date'].dt.year

# Define proper month order
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1('Australian Wildfire Analysis Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 26}),

    html.Div([
        html.Label('Select a Region:'),
        dcc.RadioItems(
            id='input-region',
            options=[{'label': r, 'value': r} for r in wildfire_df['Region'].unique()],
            value='NT',
            inline=True
        ),
    ], style={'padding': '1em'}),

    html.Div([
        html.Label('Select a Year:'),
        dcc.Dropdown(
            id='input-year',
            options=[{'label': y, 'value': y} for y in sorted(wildfire_df['Year'].unique())],
            value=2012,
            clearable=False
        ),
    ], style={'padding': '1em'}),

    html.Div([
        html.Div([
            html.H3(id='fire-area-title', style={'textAlign': 'center', 'marginBottom': '10px'}),
            dcc.Graph(id='fire-area-pie')
        ]),

        html.Div([
            html.H3(id='fire-pixel-title', style={'textAlign': 'center', 'marginBottom': '10px'}),
            dcc.Graph(id='fire-pixel-bar')
        ])
    ], style={'padding': '2em'})
])

# Callback to update charts and dynamic titles
@app.callback(
    [Output('fire-area-pie', 'figure'),
     Output('fire-pixel-bar', 'figure'),
     Output('fire-area-title', 'children'),
     Output('fire-pixel-title', 'children')],
    [Input('input-region', 'value'),
     Input('input-year', 'value')]
)
def update_graphs(selected_region, selected_year):
    filtered_df = wildfire_df[(wildfire_df['Region'] == selected_region) &
                              (wildfire_df['Year'] == selected_year)]

    # Pie chart: average fire area
    pie_df = filtered_df.groupby('Month')['Estimated_fire_area'].mean().reset_index()
    fig1 = px.pie(
        pie_df,
        values='Estimated_fire_area',
        names='Month',
        category_orders={'Month': month_order},
        color_discrete_sequence=px.colors.sequential.amp

        
    )
    fig1.update_traces(textposition='outside', textinfo='percent+label',
                       hole=0.4, marker=dict(line=dict(color='white', width=2)))
    fig1.update_layout(margin=dict(t=60, b=40, l=40, r=40))

    # Bar chart: average pixel count
    bar_df = filtered_df.groupby('Month')['Count'].mean().reset_index()
    fig2 = px.bar(
        bar_df,
        x='Month',
        y='Count',
        category_orders={'Month': month_order},
        color_discrete_sequence=['darkred']
    )
    fig2.update_layout(xaxis_title='Month', yaxis_title='Average Fire Pixel Count',
                       margin=dict(t=60, b=40, l=40, r=40))

    # Dynamic titles
    fire_area_title = f"Average Monthly Fire Area in {selected_region}, {selected_year}"
    fire_pixel_title = f"Average Monthly Fire Pixel Count in {selected_region}, {selected_year}"

    return fig1, fig2, fire_area_title, fire_pixel_title

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
