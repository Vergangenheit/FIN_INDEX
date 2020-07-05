import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import datetime
import pandas as pd
from extract_transform import transform

app = dash.Dash()

app.layout = html.Div(children=[
    html.Div(children='''
    Making a graph with dash'''),

    dcc.Input(id='input', value='', type='text'),
    html.Div(id='output-graph')
])


@app.callback(
    Output(component_id='output-graph', component_property='children'),
    [Input(component_id='input', component_property='value')])
def update_graph(input_data):
    # start = datetime.datetime(2015, 1, 1)
    # end = datetime.datetime.now()
    tseries = pd.read_csv("tseries.csv")

    return dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': tseries.Name, 'y': tseries.M, 'type': 'line', 'name': input_data},

            ],
            'layout': {
                'title': input_data
            }

        }
    )


if __name__ == '__main__':
    # tseries = pd.read_csv("tseries.csv")
    transform()
    app.run_server(debug=True)
