import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import json

from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
import plotly.express as px

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

# Data
df_trash = pd.read_csv('data\\stanoviste.csv')
with open('data\\geometry.geojson', 'r') as f:
    geojson = f.read()

# Layout of Dash App

app.layout = html.Div([
    html.Div(id="geo-map-loading-outer",
             children=[
                 dcc.Loading(
                     id="loading",
                     children=dcc.Graph(
                         id="geo-map",
                         figure={
                             "data": [],
                             "layout": dict(
                             ),
                         },
                     ),
                 )
             ],
             ),
    dcc.Input(id='num_trucks', type='number', value=1)
])


@app.callback(
    Output("geo-map", "figure"),
    [
        Input("num_trucks", "value")
    ],
)
def update_map(num_trucks):

    scatter = go.Scattermapbox(
        lat=df_trash.lat,
        lon=df_trash.long,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10,
            color='rgb(255, 0, 0)',
            opacity=0.7
        ),
        text=df_trash.street,
        hoverinfo='text'
    )

    layers = [dict(sourcetype='geojson',
                   source=json.loads(geojson),
                   color='rgb(0,0,230)',
                   type='line',
                   line=dict(width=1.5),
                   )
              ]

    layout = go.Layout(
        title='Stanoviste',
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            layers=layers,
            center=go.layout.mapbox.Center(
                lat=df_trash['lat'].mean(),
                lon=df_trash['long'].mean()
            ),
            pitch=0,
            zoom=10,
            style='light'
        ),
    )
    return {"data": [scatter], "layout": layout}


if __name__ == "__main__":
    app.run_server(debug=True)
