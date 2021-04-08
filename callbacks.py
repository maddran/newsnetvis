import dash
from dash.dependencies import Input, Output, State
from dash.dash import no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

from app import app

from summary_tab import summary_tab_content
from summary_plots import summary_figs, get_filter_options

from network_tab import network_tab_content
from network_plots import network_data, gen_network

from process_files import parse_upload, parse_preload

@app.callback(Output('output-files-upload', 'children'),
              Output('data-continue-btn', 'disabled'),
              Output('data-continue-btn', 'outline'),
              Output('upload-check', 'children'),
              Output('paths-store', 'data'),

              Input('upload-files', 'contents'),
              Input('sep-btn', 'n_clicks'),
              Input('nov-btn', 'n_clicks'),

              State('upload-files', 'filename'),
              State('upload-files', 'last_modified'),

              prevent_initial_call = True
              )
def output_preview(list_of_contents, sep_btn, nov_btn, list_of_names, list_of_dates):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    children = []
    fpaths = {}

    if list_of_contents is not None:
        res = [
                parse_upload(c, n, d) 
                for c, n, d in 
                zip(list_of_contents, list_of_names, list_of_dates)
                ]
        
        if len(res)==1:
            ftypes = [res[0][0], None]
            children = res[0][1]
        else:
            ftypes, children, fpaths = zip(*res)
            fpaths = dict(zip(ftypes, fpaths))
        
    if 'sep-btn' in changed_id:
        res = parse_preload('sep')
        children, fpaths = zip(*res)
        ftypes = ['edgelist', 'sources']
        fpaths = dict(zip(ftypes, fpaths))
    elif 'nov-btn' in changed_id:
        res = parse_preload('nov')
        children, fpaths = zip(*res)
        ftypes = ['edgelist', 'sources']
        fpaths = dict(zip(ftypes, fpaths))

    if all(ft != None for ft in ftypes) and len(set(ftypes))>1:
        disable_continue = False
        outline_continue = False
        data_status = dbc.Alert("Files pass checks! Click Continue to proceed.", 
                                color="success", style={'marginTop': '10px'})
    else:
        disable_continue = True
        outline_continue = True
        data_status = dbc.Alert("""Files failed checks! Please ensure you uploaded two 
                                files which match the criteria described above.""", 
                                color="danger", style={'marginTop':'10px'})

    return children, disable_continue, outline_continue, data_status, fpaths

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Redirect to tab~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


network_buttons = [f"{cat}-net-btn" for cat in 
                    ['region', 'country', 'language', 'source']]

summary_tab_ouputs = [Output('summary-tab', 'disabled')]
                                                
network_tab_ouputs = [Output('network-tab', 'disabled'),
                      Output('trigger-network', 'data')]

tab_change_outputs = (summary_tab_ouputs + network_tab_ouputs +
                        [Output('tabs', 'active_tab')])

@app.callback(
                tab_change_outputs,

                [Input('data-continue-btn', 'n_clicks')]+
                [Input(btn, 'n_clicks') for btn in network_buttons],
                
                State('paths-store', 'data'),
                State('filter-selections', 'data'),

                prevent_initial_call = True
             )
def on_tab_change(n_continue, 
                    n_region,
                    n_country,
                    n_language,
                    n_source, 
                    paths, 
                    filters):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    res = [no_update]*len(tab_change_outputs)

    if 'data-continue-btn' in changed_id:
        if n_continue is None:
            raise PreventUpdate
        else:
            res[0] = False
            res[-1] = 'summary-tab'

    elif any([btn in changed_id for btn in network_buttons]):
        if all([n_clicks is None for n_clicks in 
                    [n_region,
                    n_country,
                    n_language,
                    n_source]
                    ]):
            raise PreventUpdate
        else: 
            res[1] = False
            res[2] = changed_id.split('-')[0]
            res[-1] = 'network-tab'

    return tuple(res)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Populate filters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


filter_cols = ['category', 'region', 'country', 'language', 'topic']
filter_outputs = ([Output(f'include-{col}', 'options') for col in filter_cols]
                    +[Output(f'exclude-{col}', 'options') for col in filter_cols])
@ app.callback(
                filter_outputs,
                Input('paths-store', 'data')
                
)
def populate_filters(paths):
    
    if not paths:
        res = (no_update,)*len(filter_outputs)
    else:
        filter_options = get_filter_options(paths)
        filter_options = [[fo[col] for col in filter_cols] for fo in filter_options]
        res = tuple([item for sublist in filter_options for item in sublist])
    
    return res

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Update filter selection~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


filter_states = ([State(f'include-{col}', 'value') for col in filter_cols] +
                 [State(f'exclude-{col}', 'value') for col in filter_cols])
                    
@app.callback(
    Output('filter-selections', 'data'),
    [Input('apply-filters-btn', 'n_clicks'),
                   Input('filter-reset', 'n_clicks'), 
                   Input('trigger-network', 'data')],
    filter_states
)
def update_filter_selection(*inputs):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    
    inputs = list(inputs)

    n_apply = inputs.pop(0)
    n_reset = inputs.pop(0)
    net_trigger = inputs.pop(0)

    if n_reset and 'filter-reset' in changed_id:
        inputs = [None]*len(filter_states)
        return inputs
    elif ((n_apply and 'apply-filters-btn' in changed_id)
            or net_trigger):
        return inputs
    else:
        raise PreventUpdate
    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Reset dropdown values~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

filter_values = ([Output(f'include-{col}', 'value') for col in filter_cols] +
                 [Output(f'exclude-{col}', 'value') for col in filter_cols])

@app.callback(
    filter_values,
    Input('filter-reset', 'n_clicks'),

    prevent_initial_call=True
)
def reset_filter_values(n):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if n and 'filter-reset' in changed_id:
        return (None,)*len(filter_values)
    else:
        PreventUpdate

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Generate Summary Figures~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.callback(
    [Output('from-table', 'children'),
     Output('to-table', 'children')] +
    [Output(f"by-{col}-plot", 'children') 
        for col in ['region', 'language', 'country']]+
    [Output('source-net-btn', 'disabled'),
     Output('disabled-warning', 'children')],

    Input('paths-store', 'data'),
    Input('filter-selections', 'data'),
)
def generate_summary_figs(paths, filter):
    if not paths:
        raise PreventUpdate 
    else:
        if not filter:
            values = [None]*8
        else:
            values = filter

        include = values[:len(values)//2]
        exclude = values[len(values)//2:]  

        disable_source=True

        figs = summary_figs(paths, include, exclude)

        if not figs:
            tables = [dbc.Alert("""Filter selection returned and empty query! 
                                Please review your selection, or click Reset Filters 
                                to revert to defaults""",
                            color = 'danger'), '']
            figs = ['']*3
        else:
            tables = figs[0:2]
            n_sources = figs.pop(-1)
            # print(f"Num sources = {n_sources}")
            if n_sources <= 1000:
                disable_source = False
            figs = [dcc.Graph(figure=fig) for fig in figs[2:]]
        
        if disable_source:
            warning = dbc.Alert("N.B. 'Generate Source Network' has been disabled becasue "
                                "the graph would be too large to plot stably. "
                                "Please consider filtering the dataset.", 
                                color="dark")
        else:
            warning = ''

        res = tables + figs + [disable_source, warning]
        
    
    return tuple(res)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Collape filters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.callback(
    Output("filter-collapse", "is_open"),
    Input("filter-toggle", "n_clicks"),
    State("filter-collapse", "is_open"),
)
def toggle_filters(n, is_open):
    if n:
        return not is_open
    return is_open

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Produce network data~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.callback(
    Output('nodes-store', 'data'),
    Output('edges-store', 'data'),
    Output('sizecol-store', 'data'),
    Output('graph-store', 'data'),
    Output('layout-store', 'data'),
    
    Input('trigger-network', 'data'),
    Input('reset-network-btn1', 'n_clicks'),
    Input('top-in-btn1', 'n_clicks'),
    Input('top-out-btn1', 'n_clicks'),
    Input('concentric-layout1', 'n_clicks'),
    Input('cose-layout1', 'n_clicks'),
    
    State('filter-selections', 'data'),
    State('paths-store', 'data'),
    State('nodes-store', 'data'),
    
)
def generate_network_data(trigger, reset,
                            topin, topout, 
                            concentric, cose,
                            filters, paths, nodes):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if not paths:
        raise PreventUpdate
    else:
        if not filters:
            values = [None]*8
        else:
            values = filters

        include = values[:len(values)//2]
        exclude = values[len(values)//2:]

        group_map = dict(region='region', country='country', language='lang', source=None)
        nodes, edges, sizecol, graph, layout = (no_update,)*5

        if ('trigger-network' in changed_id or
                'reset-network-btn1' in changed_id):
            nodes, edges, sizecol, graph = network_data(paths, include=include, exclude=exclude,
                                        group=group_map[trigger])
        elif 'top-in-btn1' in changed_id:
            pass
        elif 'top-out-btn1' in changed_id:
            pass
        elif 'concentric-layout1' in changed_id:
            layout = 'concentric'
        elif 'cose-layout1' in changed_id:
            layout = 'cose'

        return (nodes, edges, sizecol, graph, layout)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Produce network plot~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.callback(
    Output('network-plot1', 'children'),
    
    Input('nodes-store', 'data'),
    Input('edges-store', 'data'),
    Input('sizecol-store', 'data'),
    Input('layout-store', 'data')
)
def generate_network_figs(nodes, edges, sizecol, layout):

    print(f"Producing network with {layout} layout")
    fig = gen_network(nodes, edges, sizecol, layout)

    return fig
