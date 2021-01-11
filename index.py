import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app import app
from upload_tab import upload_tab_content
from summary_tab import summary_tab_content
from network_tab import network_tab_content
import callbacks

data_tab_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("This is tab 2!", className="card-text"),
            dbc.Button("Don't click here", color="danger"),
        ]
    ),
    className="mt-3",
)

tabs = dbc.Tabs(
    [
        dbc.Tab(upload_tab_content, label="Select / Upload Data", tab_id="upload-tab"),
        dbc.Tab(summary_tab_content, label="Data Summary", disabled=True, id="summary-tab", tab_id="summary-tab"),
        dbc.Tab(network_tab_content, label="Network Plots", disabled=True, id="network-tab", tab_id="network-tab"),
    ], id='tabs', persistence = "True"
)

app.layout = dbc.Container([
                            html.H1('NewsNetVis', style={'fontWeight':'bold', 'font-size':'50px'}),
                            tabs
                            ],
                            className="p-5", fluid=True,
                            style={'width':'1400px'}
                          )

if __name__ == "__main__":
    app.run_server(debug=True)
