import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

network_cards = [dbc.Col(
                    [
                        dbc.Spinner(
                            dbc.Row(
                                [

                                ], id=f'network-plot{i}',
                            ),
                        ),
                        dbc.Row(html.H3(f"Network #{i}"), style={'position': 'absolute',
                                                                'top': 35,
                                                                'left': 25}),
                        dbc.Row(
                            dbc.ButtonGroup(
                                [
                                    dbc.Button("Reset",
                                            id=f"reset-network-btn{i}",
                                            color='primary'),
                                    dbc.Button("Top 5 by out links",
                                            id=f"top-out-btn{i}",
                                            color='primary'),
                                    dbc.Button("Top 5 by in links",
                                            id=f"top-in-btn{i}",
                                            color='primary'),
                                    dbc.Button("Concentric Layout",
                                            id=f'concentric-layout{i}',
                                            color='primary'),
                                    dbc.Button("Cose Layout",
                                            id=f'cose-layout{i}',
                                            color='primary')
                                ], vertical=False, style={'marginLeft': 15}
                            ),
                            style={'position': 'absolute',
                                    'top': 0,
                                    'left': 10}
                        ),
                    ], width = 6
                    ) 
                    for i in range(1, 3)]

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
            dbc.CardBody(
                [dbc.Row(network_cards)]
            )
        )
        
    ], id = "network-tab-content"
)

