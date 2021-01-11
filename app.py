import dash
import dash_bootstrap_components as dbc

app = dash.Dash(external_stylesheets=[dbc.themes.LUMEN])
server = app.server
server.secret_key = os.environ.get('secret_key', 'secret')
