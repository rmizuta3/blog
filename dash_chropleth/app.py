import plotly.express as px
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd
import json
import geopandas as gpd
import numpy as np

GEOJONFILE = "japan.geojson"
DATAFILE = "FEH.csv"

df = pd.read_csv(DATAFILE)
df = df[(df["性別"] == "総数") & (df["時間軸(年次)"] == "2019年") & (df["国籍"] == "移動者")]
df = df[df["value"] != "-"]
df["value"] = df["value"].astype(int)  # colorに使用するカラムは数値型に

jsonfile = gpd.read_file(GEOJONFILE)
dfjson = json.loads(jsonfile.to_json())

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div(
        html.H1('都道府県間の住所移動者(2019)',
                style={'textAlign': 'center'})
    ),
    dcc.Dropdown(
        id='selectplace',
        options=[{'label': i, 'value': i}
                 for i in df["全国・都道府県・大都市"].unique()],
        placeholder="移動先都道府県を選択",
        value="東京都"
    ),
    dcc.Loading(
        dcc.Graph(id='japanmap')
    )
])


@ app.callback(
    dash.dependencies.Output('japanmap', 'figure'),
    [dash.dependencies.Input('selectplace', 'value')])
def update_output(selectplace_value):
    selectdf = df[df["全国・都道府県・大都市"] == selectplace_value]
    fig = px.choropleth_mapbox(selectdf, geojson=dfjson, locations=selectdf['移動前の住所地'],
                               color=selectdf["value"],
                               featureidkey='properties.nam_ja',
                               color_continuous_scale="Viridis",
                               mapbox_style="carto-positron",
                               zoom=5,
                               center={"lat": 36, "lon": 138},
                               opacity=0.5,
                               labels={"value": "人数"}
                               )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
