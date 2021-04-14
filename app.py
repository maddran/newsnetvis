# import dash
from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import os

app = JupyterDash(
    external_stylesheets=[dbc.themes.LITERA],
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ],
)
server = app.server

