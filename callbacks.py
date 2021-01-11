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
from network_plots import network_plots

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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Rediect to tab~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

summary_tab_ouputs = [Output('summary-tab', 'disabled')]
                                                
network_tab_ouputs = [Output('network-tab', 'disabled'),
                      Output('trigger-network', 'data')]

tab_change_outputs = (summary_tab_ouputs + network_tab_ouputs +
                        [Output('tabs', 'active_tab')])

@app.callback(
                tab_change_outputs,

                Input('data-continue-btn', 'n_clicks'),
                Input('gen-net-btn', 'n_clicks'),
                
                State('paths-store', 'data'),
                State('filter-selections', 'data'),

                prevent_initial_call = True
             )
def on_tab_change(n_continue, n_network, paths, filters):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    res = [no_update]*len(tab_change_outputs)

    if 'data-continue-btn' in changed_id:
        if n_continue is None:
            raise PreventUpdate
        else:
            res[0] = False
            res[-1] = 'summary-tab'

    elif 'gen-net-btn' in changed_id:
        if n_network is None:
            raise PreventUpdate
        else: 
            res[1] = False
            res[2] = "DO IT"
            res[-1] = 'network-tab'
    
    return tuple(res)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Populate filters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


filter_cols = ['category', 'region', 'country', 'language']
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
    [Output('summary-table', 'children')]+
    [Output(f"by-{col}-plot", 'children') 
        for col in ['region', 'country', 'language']],

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

        # print(values)

        figs = summary_figs(paths, include, exclude)
        if not figs:
            table = dbc.Alert("""Filter selection returned and empty query! 
                                Please review your selection, or click Reset Filters 
                                to revert to defaults""",
                            color = 'danger')
            figs = ['']*3
        else:
            table = figs.pop(0)
            figs = [dcc.Graph(figure=fig) for fig in figs]
        
        res = [table] + figs
    
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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Produce network plot~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@app.callback(
    Output('network-plot', 'children'),
    
    Input('trigger-network', 'data'),
    
    State('filter-selections', 'data'),
    State('paths-store', 'data'),
    
)
def generate_network_figs(_, filters, paths):
    if not paths:
        raise PreventUpdate
    else:
        if not filters:
            values = [None]*8
        else:
            values = filters

        # print(f"Triggered network_plot with: {values}")

        include = values[:len(values)//2]
        exclude = values[len(values)//2:]

        fig = network_plots(paths, include=include, exclude=exclude,
                            group='country')

        return fig

