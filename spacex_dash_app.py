import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

app = dash.Dash(__name__)
sites = sorted(spacex_df['Launch Site'].unique())
app.layout = html.Div(style={'fontFamily': 'Arial', 'padding': '10px 30px'}, children=[
    html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 36}),
    # TASK 1: launch-site dropdown
    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': s, 'value': s} for s in sites],
                 value='ALL', placeholder='Select a Launch Site here', searchable=True),
    html.Br(),
    # TASK 2: pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),
    # TASK 3: payload range slider
    dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                    marks={i: str(i) for i in range(0, 10001, 2500)}, value=[min_payload, max_payload]),
    # TASK 4: scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

@app.callback(Output('success-pie-chart', 'figure'), Input('site-dropdown', 'value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        return px.pie(spacex_df, values='class', names='Launch Site', title='Total Successful Launches by Site')
    df = spacex_df[spacex_df['Launch Site'] == entered_site]['class'].value_counts().reset_index()
    df.columns = ['class', 'count']
    df['outcome'] = df['class'].map({1: 'Success', 0: 'Failure'})
    return px.pie(df, values='count', names='outcome', title=f'Success vs. Failed Launches for site {entered_site}',
                  color='outcome', color_discrete_map={'Success': '#2A9D8F', 'Failure': '#E63946'})

@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'), Input('payload-slider', 'value')])
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    if entered_site != 'ALL':
        df = df[df['Launch Site'] == entered_site]
    title = 'Correlation between Payload and Success for ' + ('all Sites' if entered_site == 'ALL' else entered_site)
    return px.scatter(df, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=title)

if __name__ == '__main__':
    app.run(port=8050, debug=False)
