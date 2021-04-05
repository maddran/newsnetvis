# import dash
from jupyter_dash import JupyterDash
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import os

cyto.load_extra_layouts()

# app = dash.Dash(external_stylesheets=[dbc.themes.LUMEN])
app = JupyterDash(external_stylesheets=[dbc.themes.LUMEN])

# server = app.server
# server.secret_key = os.environ.get('secret_key', 'secret')
