import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

network_tab_content = html.Div(
    [
        dcc.Store(id="network-filters"),
        dcc.Store(id='trigger-network'),
        dbc.Card(
            dbc.CardBody([
                dbc.Spinner(
                    dbc.Row(
                        [

                        ], id = 'network-plot'
                    )
                )
            ]
            )
        )
    ], id = "network-tab-content"
)

