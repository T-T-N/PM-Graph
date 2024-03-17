#https://dash.plotly.com/dash-core-components/checklist
#https://www.arduino.cc/reference/en/iot/api/#api-PropertiesV2-propertiesV2Show
#https://github.com/arduino/iot-client-py/blob/master/example/main.py
#https://blog.networktocode.com/post/using-python-requests-with-rest-apis/
#https://www.geeksforgeeks.org/how-to-update-a-plot-on-same-figure-during-the-loop/
#https://plotly.com/python/scattermapbox/
#https://medium.com/plotly/introducing-jupyterdash-811f1f57c02e
#https://www.youtube.com/watch?v=H16dZMYmvqo
#https://stackoverflow.com/questions/68866089/can-i-save-a-high-resolution-image-of-my-plotly-scatter-plot

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import requests
import numpy as np
import plotly.graph_objects as go
import time
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

CLIENT_ID = 'T9npD#!lcIh9!PYj24XHquVCg76XZ8G2'  
CLIENT_SECRET = 's!i#4#TuqSTmyB8YfLbDy3g5ITSIBcRPIf6T?3trzZvDtUkcJ2yvltBdq@FOLBrU'

oauth_client = BackendApplicationClient(client_id=CLIENT_ID)
token_url = "https://api2.arduino.cc/iot/v1/clients/token"
oauth = OAuth2Session(client=oauth_client)



app = Dash(__name__)
server = app.server

x1 = []    
y1 = []
x25 = []    
y25 = []
x10 = []    
y10 = []

config = {
  'toImageButtonOptions': {
    'format': 'png',
    'filename': 'new_plot',
    'height': 450,
    'width': 1264,
    'scale':10 
  }
}
app.layout = html.Div([
    dcc.Graph(id='live-update-graph', config=config),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # Update graph every second
        n_intervals=0
    ),
    dcc.Checklist(
        id='line-selection',
        options=[
            {'label': 'PM1.0', 'value': 'one'},
            {'label': 'PM2.5', 'value': 'twofive'},
            {'label': 'PM10', 'value': 'ten'}
        ],
        value=['one', 'twofive', 'ten']
    )
])


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('line-selection', 'value')])

def update_map(n,lines):
    token = oauth.fetch_token(
        token_url=token_url,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        include_client_id=True,
        audience="https://api2.arduino.cc/iot",
    )

    token = token['access_token']

    url = 'https://api2.arduino.cc/iot/v2/things/c3a71f6c-e861-49af-83dc-755f53f03647'
    

    headers = {
        'Authorization': f'Bearer {token}', 
    }
    
    
    response = requests.get(url, headers=headers)
    resp = response.json()
    props = resp['properties']
    time1 = props[0]['value_updated_at']
    time25 = props[2]['value_updated_at']
    time10 = props[1]['value_updated_at']
    p1 = props[0]['last_value']
    p25 = props[2]['last_value']
    p10 = props[1]['last_value'] 

    x1.append(time1)
    y1.append(p1)
    x25.append(time25)
    y25.append(p25)
    x10.append(time10)
    y10.append(p10)

    traces = []
    if 'one' in lines:
        trace1 = go.Scatter(
            x=x1,
            y=y1,
            mode='lines+markers',
            name='PM1.0',
            line=dict(color='blue')
        )
        traces.append(trace1)
    if 'twofive' in lines:
        trace2 = go.Scatter(
            x=x25,
            y=y25,
            mode='lines+markers',
            name='PM2.5',
            line=dict(color='red')
        )
        traces.append(trace2)
    if 'ten' in lines:
        trace3 = go.Scatter(
            x=x10,
            y=y10,
            mode='lines+markers',
            name='PM10',
            line=dict(color='green')
        )
        traces.append(trace3)

    layout = go.Layout(
        title='PM Concentration',
        xaxis=dict(title='Time'),
        yaxis=dict(title='μg/m^3'),
        showlegend=True
    )
    

    fig = go.Figure(data=traces, layout=layout)
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=1000)
