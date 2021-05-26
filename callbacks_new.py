import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dash import no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import itertools
import re

from app import app
from process_files import parse_upload, parse_preload
from upload_tab import upload_tab_content
from network_tab import network_tab_content, filter_cols, cats, count_params
from network_plots import network_data, gen_network
from summary_plots import summary_figs, get_filter_options, get_data_counts

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Toggle navbar for small screens~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Set page content~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.callback(Output('page-content', 'children'),
              Output('select-data-btn', 'active'),
              Output('network-plots-btn', 'active'),
              Output('layout-store', 'data'),

              Input('url', 'pathname'),

              State('layout-store', 'data'),
              State('page-content', 'children')

        )
def display_page(pathname, layouts, current_layout):
    data_active = no_update
    netplots_active = no_update

    if any(pathname == path for path in ['/', '', '//']):
        data_active, netplots_active = [True, False]
        if layouts['data'] != None:
            layouts['plots'] = current_layout
            content = layouts['data']
        else:
            content = upload_tab_content
            layouts['data'] = content

    elif pathname == '/netplots':
        data_active, netplots_active = [False, True]
        layouts['data'] = current_layout
        if layouts['plots'] != None:
            content = layouts['plots']
        else:
            content = network_tab_content
            layouts['plots'] = content
    
    return (content, 
            data_active, netplots_active,
            layouts)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Verify files~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.callback(Output('output-files-upload', 'children'),
              Output('data-continue-btn', 'disabled'),
              Output('data-continue-btn', 'outline'),
              Output('network-plots-btn', 'disabled'),
              Output('upload-check', 'children'),
              Output('paths-store', 'data'),

              Input('upload-files', 'contents'),
              Input('sep-btn', 'n_clicks'),
              Input('nov-btn', 'n_clicks'),
              Input('jan-btn', 'n_clicks'),

              State('upload-files', 'filename'),
              State('upload-files', 'last_modified'),

              prevent_initial_call=True,
              )
def output_preview(list_of_contents,
                   sep_btn, nov_btn, jan_btn,
                   list_of_names, list_of_dates):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    children = []
    fpaths = {}

    if list_of_contents is not None:
        res = [
            parse_upload(c, n, d)
            for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)
        ]

        if len(res) == 1:
            ftypes = [res[0][0], None]
            children = res[0][1]
        else:
            ftypes, children, fpaths = zip(*res)
            fpaths = dict(zip(ftypes, fpaths))

    if (any(btn in changed_id for btn in ['sep-btn', 'nov-btn', 'jan-btn']) and
        any(click > 0 for click in [sep_btn, nov_btn, jan_btn])):

        res = parse_preload(changed_id.split('-')[0])
        children, fpaths = zip(*res)
        ftypes = ['edgelist', 'sources']
        fpaths = dict(zip(ftypes, fpaths))
    else:
        raise PreventUpdate

    if all(ft != None for ft in ftypes) and len(set(ftypes)) > 1:
        disable_continue = False
        outline_continue = False
        disable_netplot = False
        data_status = dbc.Alert("Files pass checks! Click Continue to proceed.",
                                color="success", style={'marginTop': '10px'})
    
    else:
        disable_continue = True
        outline_continue = True
        disable_netplot = True
        data_status = dbc.Alert("""Files failed checks! Please ensure you uploaded two 
                                files which match the criteria described above.""",
                                color="danger", style={'marginTop': '10px'})

    return children, disable_continue, outline_continue, disable_netplot, data_status, fpaths

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Populate filters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

filter_outputs = [
                    [Output(f'include-{col}{i}', 'options') for col in filter_cols]
                  + [Output(f'exclude-{col}{i}', 'options') for col in filter_cols]
                  for i in range(1,3)
                 ]
filter_outputs = list(itertools.chain.from_iterable(filter_outputs))

@ app.callback(
    filter_outputs,
    Input('paths-store', 'data'),
)
def populate_filters(paths):
    if not paths:
        res = (no_update,)*len(filter_outputs)
    else:
        filter_options = get_filter_options(paths)
        filter_options = [[fo[col] for col in filter_cols]
                          for fo in filter_options]
        res = tuple([item for sublist in filter_options for item in sublist]*2)
    

    return res


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Reset dropdown values~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
filter_values = [
    [Output(f'include-{col}{i}', 'value') for col in filter_cols]
    + [Output(f'exclude-{col}{i}', 'value') for col in filter_cols]
    for i in range(1, 3)
    ]

filter_values = list(itertools.chain.from_iterable(filter_values))

@app.callback(
    filter_values,
    [Input(f'reset-filters-btn{i}', 'n_clicks') for i in range(1,3)],
    prevent_initial_call=True
)
def reset_filter_values(*n):

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if changed_id and len(changed_id) > 1:
        net_number = int(changed_id.split('.')[0][-1])
    else:
        raise PreventUpdate

    res = [no_update]*(len(filter_values)//2)
    if n[net_number -1] and 'reset-filters-btn' in changed_id:
        if net_number == 1:
            res = [None]*(len(filter_values)//2) + res
        elif net_number == 2:
            res = res + [None]*(len(filter_values)//2)
    else:
        PreventUpdate

    return tuple(res)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Toggle filter collapse~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.callback(
    [Output(f"filter-collapse{i}", "is_open") for i in range(1, 3)],
    [Input(f"collapse-filter-btn{i}", "n_clicks") for i in range(1, 3)],
    [State(f"filter-collapse{i}", "is_open") for i in range(1, 3)]
)
def toggle_filter_collapse(n1, n2, is_open1, is_open2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    res = [no_update, no_update]
    if "collapse-filter-btn1" in changed_id:
        res[0] = not is_open1
    elif "collapse-filter-btn2" in changed_id:
        res[1] = not is_open2
    return tuple(res)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Store Filter Selections~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

filter_inputs = [
                    [Input(f'include-{col}{i}', 'value') for col in filter_cols]
                  + [Input(f'exclude-{col}{i}', 'value') for col in filter_cols]
                  + [Input(f'include-{col}{i}', 'options') for col in filter_cols]
                  + [Input(f'exclude-{col}{i}', 'options') for col in filter_cols]
                  for i in range(1,3)
                 ]

count_store = [Output(f'counts-store-{i}', 'data')for i in range(1, 3)]

filter_inputs = list(itertools.chain.from_iterable(filter_inputs))

@app.callback(
    [Output('filter-store1', 'data'),
    Output('filter-store2', 'data')]+count_store,

    filter_inputs,

    State('paths-store', 'data')
)
def update_filter_selection(*inputs):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    inputs = list(inputs)
    paths = inputs.pop(-1)

    if changed_id and len(changed_id)>1:
        net_number = int(changed_id.split('.')[0][-1])
    else:
        raise PreventUpdate

    if net_number == 1:
        inputs = inputs[:len(inputs)//2]
        inputs = inputs[:len(inputs)//2]
    elif net_number == 2:
        inputs = inputs[len(inputs)//2:]
        inputs = inputs[:len(inputs)//2]
    
    filter_res = [no_update, no_update]
    counts_res = [no_update, no_update]

    filter_state = None
    include = None
    exclude = None

    if 'value' in changed_id:
        filter_state = {
            'include': dict(zip(filter_cols, inputs[:len(inputs)//2])),
            'exclude': dict(zip(filter_cols, inputs[len(inputs)//2:])),
        }
        filter_res[net_number-1] = filter_state

        include = (filter_state['include'].values() if (filter_state and any(
                        filter_state['include'].values())) else None)
        exclude = (filter_state['exclude'].values() if (filter_state and any(
            filter_state['exclude'].values())) else None)
        
    if any([include, exclude]):    
        counts_res[net_number-1] = get_data_counts(paths, include, exclude)
    else:
        counts_res = [get_data_counts(paths, include, exclude)]*2
    
    res = filter_res+counts_res
    
    return tuple(res)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Update counts~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

count_outputs = [
    [Output(f"{param}-count{i}", "children")for param in count_params]
    for i in range(1, 3)
]

source_button_out = [[Output(f'source-net-btn{i}', 'disabled'),
                      Output(f'disabled-warning{i}', 'children')]
                     for i in range(1, 3)]

count_inputs = [Input(f'counts-store-{i}', 'data')for i in range(1, 3)]
count_LU = ['article', 'country', 'lang', 'sources']

for i in range(0,2):
    @app.callback(
        count_outputs[i]+source_button_out[i],
        count_inputs[i],
    )
    def update_counts(*inputs):

        inputs = list(inputs)

        counts = inputs[0]

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        if changed_id and len(changed_id) > 1:
            len_out = len(count_outputs[0]) + len(source_button_out[0])
            res = [no_update]*len_out
            out_ = [counts[param] for param in count_LU]
            res[0:4] = [format_num(o) for o in out_]
            if res[3] > 1e3:
                res[4:] = [True, dbc.Alert("N.B. 'Generate Source Network' has been disabled becasue "
                                                    "the graph would be too large to plot stably. "
                                                    "Please consider filtering the dataset.",
                                                    color="dark")]
            else:
                res[4:] = [False, '']
        else:
            raise PreventUpdate

        return tuple(res)

def format_num(num):
    if num >= 1e6:
        return f"{round(num/1e6, 2)}M"
    elif num >= 1e4:
        return f"{round(num/1e4, 2)}k"
    else:
        return num
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Produce Network Data~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

plot_control_inputs = [
    [Input(f"reset-network-btn{i}", "n_clicks"),
    Input(f"top-out-btn{i}", "n_clicks"),
    Input(f"top-in-btn{i}", "n_clicks"),
    Input(f'concentric-layout{i}', "n_clicks"),
    Input(f'cose-layout{i}', "n_clicks")]+
    [Input(f"{cat}-net-btn{i}", 'n_clicks') for cat in cats]+
    [Input(f'filter-store{i}', 'data')]
    for i in range(1,3)
]
plot_control_inputs = list(itertools.chain.from_iterable(plot_control_inputs))

network_data_ouputs = [[Output(f'plot-group-store{i}', 'data'),
                       Output(f'nodes-store{i}', 'data'),
                       Output(f'edges-store{i}', 'data'),
                       Output(f'sizecol-store{i}', 'data'),
                       Output(f'graph-store{i}', 'data'),
                       Output(f'network-layout-store{i}', 'data')]
                       for i in range(1, 3)]
network_data_ouputs = list(itertools.chain.from_iterable(network_data_ouputs))

network_states = ([State(f'plot-group-store{i}', 'data') for i in range(1, 3)]+
                 [State(f'network-layout-store{i}', 'data') for i in range(1, 3)]+
                 [State('paths-store', 'data')])

@app.callback(
    network_data_ouputs,
  
    plot_control_inputs,

    network_states,
)
def generate_network_data(*inputs):
    inputs = list(inputs)
    paths = inputs.pop(-1)
    plot_layout = inputs[-2:]
    inputs = inputs[:-2]
    plot_group = inputs[-2:]
    inputs = inputs[:-2]

    if not paths:
        raise PreventUpdate

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if changed_id and len(changed_id) > 1:
        net_number = int(changed_id.split('.')[0][-1])
    else:
        raise PreventUpdate

    if net_number == 1:
        inputs = inputs[:len(inputs)//2]
    elif net_number == 2:
        inputs = inputs[len(inputs)//2:]

    filters = inputs.pop(-1)

    if not filters:
        include = [None]*len(filter_cols)
        exclude = [None]*len(filter_cols)
    else:
        include = filters['include'].values()
        exclude = filters['exclude'].values()

    if any(cat in changed_id for cat in cats):
        active_btn = [cat for cat in cats if cat in changed_id][0]
    elif plot_group[net_number-1]:
        active_btn = plot_group[net_number-1]
    else:
        raise PreventUpdate

    net_data = [no_update]*(len(network_data_ouputs)//2)
    net_data[0] = active_btn

    group_map = dict(region='region', country='country',
                     language='lang', source=None)
    net_data[1:5] = network_data(paths, include=include, exclude=exclude,
                       group=group_map[active_btn])

    if 'cose' in changed_id:
        net_data[-1] = 'cose'
    elif 'concentric' in changed_id:
        net_data[-1] = 'concentric'
    elif plot_layout[net_number-1]:
        net_data[-1] = plot_layout[net_number-1]
    else:
        net_data[-1] = 'concentric'
    
    res=[no_update]*len(network_data_ouputs)
    if net_number == 1:
        res[:len(res)//2] = net_data
    elif net_number == 2:
        res[len(res)//2:] = net_data

    return tuple(res)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Produce network plot~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

network_plot_inputs = [[Input(f'nodes-store{i}', 'data'),
                        Input(f'edges-store{i}', 'data'),
                        Input(f'sizecol-store{i}', 'data'),
                        Input(f'network-layout-store{i}', 'data'),
                        Input(f'graph-store{i}', 'data')]
                       for i in range(1, 3)]
# network_plot_inputs = list(itertools.chain.from_iterable(network_plot_inputs))

for i in range(0,2):
    @app.callback(
        Output(f'network-plot{i+1}','children'),
        Output(f'plot-desc-{i+1}', 'children'),

        network_plot_inputs[i],
        State(f'plot-group-store{i+1}', 'data'),
        State(f'filter-store{i+1}', 'data')
    )
    def generate_network_figs(*inputs):

        inputs = list(inputs)

        filters = inputs.pop(-1)
        if not filters:
            include = "all"
            exclude = "none"
        else:
            include = filters['include'].values()
            include = list(itertools.chain.from_iterable([l for l in include if l]))
            include = ', '.join(str.capitalize(s) for s in include if s)

            exclude = filters['exclude'].values()
            exclude = list(itertools.chain.from_iterable([l for l in exclude if l]))
            exclude = ', '.join(str.capitalize(s) for s in exclude if s)

        if len(include) == 0:
            include = "all"
        if len(exclude) == 0:
            exclude = "none"

        plot_group = inputs.pop(-1)
        layout = inputs[3]

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        if changed_id and len(changed_id) > 1:
            print(f"Num nodes = {len(inputs[0])}")
            if len(inputs[0]) >= 1e3:
                res = [html.H5("Too many nodes in current selection!"
                                    "Please consider either filtering the dataset or"
                                    " selecting a different level of aggregation.",
                                style={'height': '200px',
                                       'text-align': 'center',
                                       'padding': '100px',
                                       'width': '100%',
                                       'color':'red',
                                       'font-size': '20px',
                                       }), None]
            else:
                desc = (f"Current Plot : {str.capitalize(plot_group)} network // "
                        f"{str.capitalize(layout)} layout // Includes {include} // "
                        f"Excludes {exclude}"
                        )
                res = [gen_network(*inputs[:-1]), desc]
            return res
        else:
            raise PreventUpdate

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Update plot layout~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# top_by_degree_inputs = [Input(id = f'')]
