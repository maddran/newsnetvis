import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html


upload_div = html.Div([
    html.H5("Or, upload data files below:", className="upload-text"),
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
        html.H5("Select one of the preloaded datasets below:", id="preload-text"),
        dbc.Button("Sep 2020", outline=False, color="primary", id='sep-btn', 
                   className="mr-1", n_clicks=0),
        dbc.Button("Nov 2020", outline=False, color="primary", id='nov-btn', 
                   disabled=True, className="mr-1", n_clicks=0),
        dbc.Button("Jan 2021", outline=False, color="primary", id='jan-btn',
                   disabled=True, className="mr-1", n_clicks=0)
    ])

upload_tab_content = dbc.Row(
            [
                dbc.Col(
                    [
                        preload_div,
                        html.Hr(),
                        upload_div,
                        html.Hr(),
                        dbc.Button("Continue", color="primary", id="data-continue-btn",
                                    block=True, outline = True, disabled=True, href='/netplots'),
                        html.Div(id='upload-check')
                    ], id="select_col", width = 4
                ),
                dbc.Col(
                    dbc.Spinner(
                        [
                            html.Div(id='output-files-upload',
                                        style={"height": "500px"},
                                        className="p-3"),
                        ]
                    ), id="table_col", width=5, style={"background-color": "rgba(10,30,100,0.1)"}
                )
            ], className = "vh-100 p-4", 
        )
