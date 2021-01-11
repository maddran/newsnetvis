import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


upload_div = html.Div([
    html.H3("Or, upload data files below:", className="upload-text"),
    html.Ul([
        html.Li("Source List: CSV file containing metadata of sources used to produce dataset (with latitude and longitude)"),
        html.Li(
            "Edge List: CSV file produced by NewsNet describing network to be plotted.")
    ]),
    dcc.Upload(
        id='upload-files',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files (csv)')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'marginLeft': '0px',
            'marginBottom':'5px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    )
])

preload_div = html.Div(
    [
        html.H3("Select one of the preloaded datasets below:", className="preload-text"),
        dbc.Button("Sep 2020", outline=False, color="primary", id='sep-btn', 
                   className="mr-1", n_clicks=0),
        dbc.Button("Nov 2020", outline=False, color="primary", id='nov-btn', 
                   disabled=True, className="mr-1", n_clicks=0)
    ])

upload_tab_content = html.Div(
    [
        dcc.Store(id="paths-store"),
        dbc.Card(
            dbc.CardBody(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                preload_div,
                                html.Hr(),
                                upload_div,
                                html.Hr(),
                                dbc.Button("Continue", color="primary", id="data-continue-btn",
                                            block=True, outline = True, disabled=True),
                                html.Div(id='upload-check')
                            ], id="select_col",
                        ),
                        dbc.Col(
                            dbc.Spinner(
                                [
                                    html.Div(id='output-files-upload',
                                             style={"height": "300px"}),
                                ]
                            ), id="table_col", width=6 
                        )
                    ], style={"height": "100%"}
                )

            ), style={"height": "100vh"}
        )
        
    ])
