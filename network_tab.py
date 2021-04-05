import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

network_tab_content = html.Div(
    [
        dcc.Store(id="network-filters"),
        dcc.Store(id='trigger-network'),
        dcc.Store(id='nodes-store'),
        dcc.Store(id='edges-store'),
        dcc.Store(id='sizecol-store'),
        dcc.Store(id='graph-store'),

        dcc.Store(data = 'concentric', id='layout-store'),
        dbc.Card(
            dbc.CardBody([
                html.Div(
                    dbc.Spinner(
                        dbc.Row(
                            [

                            ], id='network-plot', 
                        ), 
                    ), style={'position': 'relative'}
                ),
                dbc.Row(
                    dbc.ButtonGroup(
                        [
                            dbc.Button("Reset", 
                                        id="reset-network-btn",
                                        color='primary'),
                            dbc.Button("Top 5 by out links",
                                        id="top-out-btn", 
                                        color='primary'),
                            dbc.Button("Top 5 by in links",
                                        id="top-in-btn", 
                                        color='primary'),
                            dbc.Button("Concentric Layout",
                                        id='concentric-layout',
                                        color='primary'),
                            dbc.Button("Cose Layout",
                                       id='cose-layout',
                                       color='primary')
                        ], style={'marginLeft':15}
                        ), 
                        style={'position': 'absolute', 
                                'top' : 10,
                                'left' : 10}
                ),
            ]
            )
        )
    ], id = "network-tab-content"
)

