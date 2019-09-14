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

from model.model import State


class DashApp:

    def __init__(self, state):

        app = dash.Dash(
            __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
        )
        server = app.server

        # Plotly mapbox public token
        mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"

        # Data

        # df_trash = state.get_active_bins_positions()

        # Layout of Dash App

        app.layout = html.Div([
            html.Div(
                children=dcc.Graph(
                                 id="geo-map",
                                 figure={
                                     "data": [],
                                     "layout": dict(
                                     ),
                                 },
                                 style={'height': '720px'}
                             ),
                     ),
            html.Button('Next step', id='simulation_step')
        ])


        # app.layout = html.Div([
        #     html.Div(id="geo-map-loading-outer",
        #              children=[
        #                  dcc.Loading(
        #                      id="loading",
        #                      children=dcc.Graph(
        #                          id="geo-map",
        #                          figure={
        #                              "data": [],
        #                              "layout": dict(
        #                              ),
        #                          },
        #                      ),
        #                  )
        #              ],
        #              ),
        #     html.Button('Next step', id='simulation_step')
        # ])

        @app.callback(
            Output("geo-map", "figure"),
            [
                Input("simulation_step", "n_clicks")
            ],
        )
        def update_map(n_clicks):
            df_trash = state.get_active_bins_positions()
            trucks = state.trucks
            truck_ids = set([truck.id_ for truck in trucks])
            truck_pos = [(truck.id_, *state.id_to_pos(truck.pos)) for truck in trucks]

            scatter_trash = go.Scattermapbox(
                lat=df_trash.lat,
                lon=df_trash.long,
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=7,
                    color='rgb(255, 0, 0)',
                    opacity=0.7
                ),
                text=df_trash.street,
                hoverinfo='text'
            )

            scatter_trucks = go.Scattermapbox(
                lat=[pos[1] for pos in truck_pos],
                lon=[pos[2] for pos in truck_pos],
                mode='markers',
                marker=go.scattermapbox.Marker(
                    size=12,
                    color='rgb(0, 255, 0)',
                    opacity=0.7
                ),
                text=["Truck {0}".format(truck.id_) for truck in trucks],
                hoverinfo='text'
            )

            state.next()
            next_trucks = state.trucks
            next_truck_pos = [(truck.id_, *state.id_to_pos(truck.pos)) for truck in next_trucks if truck.id_ in truck_ids]
            truck_pos.sort(key=lambda t: t[0])
            next_truck_pos.sort(key=lambda t: t[0])

            successive_pos = [((pos_1[1], pos_1[2]), (pos_2[1], pos_2[2]))
                              for pos_1, pos_2 in zip(truck_pos, next_truck_pos)]
            routes = [{"type": "Feature", "geometry": state.get_route(pos_from, pos_to)} for pos_from, pos_to in successive_pos]
            routes_dict = {"type": "FeatureCollection", "features": routes}
            routes_gjson = json.dumps(routes_dict)

            layers = [dict(sourcetype='geojson',
                           source=routes_dict,
                           color='rgb(0,0,255)',
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

            return {"data": [scatter_trash, scatter_trucks], "layout": layout}

        self._app = app

    def run(self, debug=True):
        self._app.run_server(debug=debug)


if __name__ == "__main__":
    df = pd.read_csv("distance_matrix.csv", header=None, delimiter="\t")
    df = df.iloc[:, :-1]
    state = State(df.values, 10)
    app = DashApp(state)
    app.run(debug=True)
