import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dash import no_update
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State

import itertools

from app import app
from process_files import parse_upload, parse_preload
from upload_tab import upload_tab_content
from network_tab import network_tab_content, filter_cols, cats
from network_plots import network_data, gen_network
from summary_plots import summary_figs, get_filter_options

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
                  for i in range(1,3)
                 ]

filter_inputs = list(itertools.chain.from_iterable(filter_inputs))

@app.callback(
    Output('filter-store1', 'data'),
    Output('filter-store2', 'data'),

    filter_inputs

)
def update_filter_selection(*inputs):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    inputs = list(inputs)

    if changed_id and len(changed_id)>1:
        net_number = int(changed_id.split('.')[0][-1])
    else:
        raise PreventUpdate

    if net_number == 1:
        inputs = inputs[:len(inputs)//2]
    elif net_number == 2:
        inputs = inputs[len(inputs)//2:]
    
    # n_reset = inputs.pop(-1)
    res = [no_update, no_update]

    # if n_reset and 'reset-filters' in changed_id:
    #     filter_state = {
    #         'include': dict(zip(filter_cols, [None]*len(filter_cols))),
    #         'exclude': dict(zip(filter_cols, [None]*len(filter_cols))),
    #     }
    if (any(match in changed_id for match in ['include', 'exclude'])):
        filter_state = {
            'include': dict(zip(filter_cols, inputs[:len(inputs)//2])),
            'exclude': dict(zip(filter_cols, inputs[len(inputs)//2:])),
        }
    else:
        raise PreventUpdate

    res[net_number-1] = filter_state
    return tuple(res)
    

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
# network_states = list(itertools.chain.from_iterable(network_states))


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
network_plot_inputs = list(itertools.chain.from_iterable(network_plot_inputs))

@app.callback(
    Output('network-plot1','children'),
    Output('network-plot2','children'),

    network_plot_inputs,

    # network_states,
)
def generate_network_figs(*inputs):

    inputs = list(inputs)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if changed_id and len(changed_id) > 1:
        net_number = int(changed_id.split('.')[0][-1])
    else:
        raise PreventUpdate

    if net_number == 1:
        inputs = inputs[:len(inputs)//2]
    elif net_number == 2:
        inputs = inputs[len(inputs)//2:]

    res = [no_update]*2
    res[net_number-1] = gen_network(*inputs[:-1])
    return res
