import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

filter_cols = ['category', 'region', 'country', 'language']

include_dropdowns = [dbc.Col(dcc.Dropdown(options=[], 
                                            multi=True, 
                                            id=f'include-{col}',
                                            placeholder=f'Select {col}'))
                    for n, col in enumerate(filter_cols)]

exclude_dropdowns = [dbc.Col(dcc.Dropdown(options=[],
                                         multi=True,
                                         id=f'exclude-{col}',
                                         placeholder=f'Select {col}'))
                    for n, col in enumerate(filter_cols)]

filter_card = dbc.Card([
                    dbc.CardHeader(
                                dbc.Row([
                                    dbc.Button(
                                        f"Show/Hide Filters",
                                        color='secondary',
                                        id=f"filter-toggle",
                                        style={"margin": "10px"}),
                                    dbc.Button(
                                        f"Reset Filters",
                                        color='primary',
                                        id=f"filter-reset",
                                        style={"margin":"10px", "marginLeft":"0px"}),
                                ])
                            ),
                    dbc.Collapse(
                        dbc.CardBody(
                            [
                                html.H5("Include the following (default is all):"),
                                dbc.Row(include_dropdowns, id='include-input',
                                        style={'marginBottom': '10px'}),
                                html.Hr(),
                                html.H5("Exclude the following (default is none):"),
                                dbc.Row(exclude_dropdowns, id='exclude-input'),#, style={'height': "100px"}),
                            ]
                        ), id='filter-collapse', is_open=True
                    )
                ], style={'marginBottom': '10px'})


daily_plot_tabs = dbc.Tabs(
    [
        dbc.Tab(html.Div(id=f"by-{col}-plot"), 
                label=f"Daily Article Count by {col.capitalize()}", 
                tab_id=f"by-{col}-tab") 
        for col in ['region', 'language', 'country']
    ], style={'width':'100%', 'fontSize':14})

summary_tab_content = html.Div(
    [
        dcc.Store(id="edges-store"),
        dcc.Store(id="filter-selections"),
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H4("Filter data below (scroll for summary tables and plots)"),

                ]),

                filter_card,

                dbc.Row([
                    dbc.Col(dbc.Button("Apply Filters", color='primary', id="apply-filters-btn",
                                    block=True, outline=False, disabled=False), width = 6),
                         
                    dbc.Col(dbc.Button("Generate Network", color='primary', id="gen-net-btn",
                                    block=True, outline=False, disabled=False), width = 6)
                        ]),

                dbc.Row(
                    [
                        dbc.Col(
                            [ 
                                html.H5("Summary Table"),
                                dbc.Spinner([
                                    html.Div(id='summary-table', style={'height':"300px"})
                                ])
                            ], width=6),
                        dbc.Col(
                            [
                                html.H5("Drill-down Table"),
                                dbc.Spinner([
                                   html.Div(id='drill=table', style={'height':"300px"}) 
                                ])
                            ], width=6),
                    ], style={'marginTop':'20px'}
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Spinner([
                                    daily_plot_tabs,
                                ]
                                    )
                            ], width=12),
                    ], style=dict(marginTop=10)
                )  
            ]), style={'height': '2000px'}
        )
    ],
)
