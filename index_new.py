from jupyter_dash import JupyterDash as Dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, server
import callbacks_new
from upload_tab import upload_tab_content
from network_tab import network_tab_content


navbg = {'backgroundColor': 'rgba(20,20,20,.5)'}
nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Select / Upload Data", active=True, href="/",
                                id='select-data-btn')),
        dbc.NavItem(dbc.NavLink("Network Plots", disabled=True, href="/netplots",
                                id='network-plots-btn')),
        dbc.NavItem(dbc.NavLink("Network Details", disabled=True, href="/netdetails",
                                id='network-details-btn')),
    ],
    pills=True,
    # vertical=False,
)


navbar = dbc.Navbar(
    [
        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("NewsNetVis", className="ml-2 ")),
                ],
                align="center",
                no_gutters=True,
            ),
            href="/",
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
        dbc.Collapse(nav, id="navbar-collapse", navbar=True)
    ],
    light=True
)

url_nav_content = dbc.Container(
    [
        dcc.Location(id='url', refresh=False),
        navbar,
        html.Div(id="page-content"),
        dcc.Store(id="paths-store"),
        dcc.Store(id="data-store"),
        dcc.Store(data={"data": None, "plots": None}, id="layout-store"),

    ],
    className="p-0",
    fluid=True
)

app.validation_layout = html.Div([
    url_nav_content,
    upload_tab_content,
    network_tab_content,
])

app.layout = url_nav_content



if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
