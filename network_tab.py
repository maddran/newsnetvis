import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

plot_controls = [dbc.ButtonGroup(
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
    ], vertical=False, className="ml-3"
) for i in range(1, 3)]

filter_cols = ['category', 'region', 'country', 'language', 'topic']
dropdowns = [
    [
        [dcc.Dropdown(options=[],
                        multi=True,
                        id=f'include-{col}{i}',
                        placeholder=f'Select {col}',
                        className="mt-2")
         for n, col in enumerate(filter_cols)],
        [dcc.Dropdown(options=[],
                        multi=True,
                        id=f'exclude-{col}{i}',
                        placeholder=f'Select {col}',
                        className="mt-2")
         for n, col in enumerate(filter_cols)]
    ]
    for i in range(1, 3)
]

cats = ['region', 'country', 'language', 'source']
disabled = dict(zip(cats, [False, False, False, True]))

gen_plot_btns = [
                    dbc.Col([
                        dbc.Button(f"Generate {cat.capitalize()} Network",
                                    color='primary',
                                    id=f"{cat}-net-btn{i}",
                                    block=True,
                                    disabled=disabled[cat],
                                    className="mb-1") 
                        for cat in cats
                    ]+[html.Div(id=f'disabled-warning{i}')])
                    
                    for i in range(1,3)
                ]

count_params = ['articles', 'countries', 'languages', 'sources']
data_counts = [dbc.Row([
        dbc.Card([
            dbc.CardHeader(f"# {param}"),
            dbc.CardBody(html.H5(id=f"{param}-count{i}"), 
                    className='p-2 text-center'),
            ],
            className='w-40 m-2')
        for param in count_params
],className='d-flex justify-content-center') for i in range(1, 3)]

control_collapse = [
                        dbc.Collapse([
                            dbc.Row([
                                dbc.Col(
                                    [html.H6('Include (default is all):')] +
                                    dropdowns[i-1][0], width = 4
                                ),
                                dbc.Col(
                                    [html.H6('Exclude (default is none):')] +
                                    dropdowns[i-1][1], width = 4
                                ),
                                gen_plot_btns[i-1]                                    
                                        
                            ], align='center')
                        ], id=f'filter-collapse{i}', is_open=True)
                        for i in range(1, 3)
                    ]

network_plots = [
                    dbc.Col(
                        [
                            dcc.Store(id=f'plot-group-store{i}'),
                            dcc.Store(id=f'nodes-store{i}'),
                            dcc.Store(id=f'edges-store{i}'),
                            dcc.Store(id=f'sizecol-store{i}'),
                            dcc.Store(id=f'graph-store{i}'),
                            dcc.Store(id=f'filter-store-{i}'),
                            dbc.Spinner(
                                dcc.Store(id=f'counts-store-{i}'),
                                fullscreen=True, fullscreen_style={'opacity': '.2'}
                                ), 
                            dbc.Container([
                                dbc.Row([html.H4(f"Network #{i}",
                                                 className="ml-3 mt-1 align-middle"),
                                         html.P("Current Plot : None", 
                                                id=f'plot-desc-{i}',
                                                className="ml-3 mt-2 align-middle",
                                                style={'font-family':'sans-serif',
                                                       'color': 'rgb(0, 150, 200)'})
                                         ]),
                                html.Div(
                                    control_collapse[i-1], className="w-100 p-1"),
                                dbc.Row([
                                    dbc.Col(data_counts[i-1],width=8,
                                            className=""),
                                    dbc.Col([
                                        dbc.Button(
                                            "Show/Hide Controls",
                                            id=f"collapse-filter-btn{i}",
                                            className="w-100 mt-0",
                                            color="primary",
                                        ),
                                        dbc.Button(
                                            "Reset Filters",
                                            id=f"reset-filters-btn{i}",
                                            className="w-100 mt-2",
                                            color="primary",
                                        )], className="align-self-center"),
                                ]),                                
                                        ],className='p-3',
                                        style={'background': 'rgba(100,100,100,.1)',
                                                'border-radius': '25px'}),

                            dbc.Row(
                                html.Div([
                                    dbc.Spinner(
                                        dbc.Row(
                                            [
                                                html.Div("Make selections above to draw plot",
                                                        style={'height':'200px',
                                                                'text-align':'center',
                                                                'padding':'100px',
                                                                'width':'100%',
                                                                'font-size':'20px',
                                                                }),
                                            ], id=f'network-plot{i}', className='ml-3',
                                        ), id=f'network-spinner{i}'
                                    ),
                                    html.Div(plot_controls[i-1], style={'position': 'absolute',
                                                                        'left': '3px',
                                                                        'top': '15px',
                                                                        })
                                ], className='w-100', style={'position': 'relative'})
                            )
                            
                            
                        ], className='ml-5' if i > 1 else 'ml-0'
                    )
                for i in range(1, 3)]


summary_figs = dbc.Row(id='summary-figs')
summary_collapse = dbc.Collapse(summary_figs, is_open=True)

network_tab_content =  html.Div(
    [
        dcc.Store(id="filter-store1"),
        dcc.Store(id="filter-store2"),
        dcc.Store(data='concentric', id='network-layout-store1'),
        dcc.Store(data='concentric', id='network-layout-store2'),
        dbc.Row(summary_collapse),
        dbc.Container(dbc.Row(network_plots), fluid=True), 
        
    ], id = "network-tab-content", className='p-4'
)

