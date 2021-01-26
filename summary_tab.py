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
                                        className="mr-1"),
                                    dbc.Button(
                                        f"Reset Filters",
                                        color='primary',
                                        id=f"filter-reset",
                                        className="mr-1"),
                                    dbc.Button(
                                        "Apply Filters", 
                                        color='primary', 
                                        id="apply-filters-btn",
                                        className="mr-1")
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
    ], style={'width':'100%', 'fontSize':14, 'height':'50%'})

cats = ['region', 'country', 'language', 'source']
disabled = dict(zip(cats, [False, False, False, True]))
network_buttons = []
for cat in cats:
    button = dbc.Button(f"Generate {cat} Network",
                        color='primary',
                        id=f"{cat}-net-btn",
                        block=True,
                        disabled=disabled[cat],
                        className="mb-1")

    network_buttons.append(html.Div(button))
network_buttons.append(html.Div(id='disabled-warning'))

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

    
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Spinner([
                                    daily_plot_tabs,
                                ]
                                )
                            ], width=8),
                        dbc.Col(network_buttons, width=4),
                    ], align="center", style=dict(marginTop=10)
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [ 
                                html.H5("Top 20 by Article Count"),
                                dbc.Spinner([
                                    html.Div(id='from-table', style={'height':"300px"})
                                ])
                            ], width=6),
                        dbc.Col(
                            [
                                html.H5("Top 20 by Incoming Links"),
                                dbc.Spinner([
                                   html.Div(id='to-table', style={'height':"300px"}) 
                                ])
                            ], width=6),
                    ], style={'marginTop': '20px', 'marginBottom': '20px'}
                ),
                
            ]), style={'height': '2000px'}
        )
    ],
)
