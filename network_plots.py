import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt 
import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
import dash_html_components as html

import pandas as pd
import numpy as np
from datetime import timedelta

from summary_plots import get_full_data, load_files

def sum_dicts(x,y,sub=0):
    return {k: x.get(k, 0) + (-1*sub)*y.get(k, 0) for k in set(x) | set(y)}

def node_size_col(G):
    in_degree = dict(G.in_degree(weight='count'))
    out_degree = dict(G.out_degree(weight='count'))

    selfloops = list(nx.selfloop_edges(G, data=True))
    selfloops = dict([(l[0], 2*l[2]['count']) for l in selfloops])

    total_degree = sum_dicts(dict(G.degree(weight='count')), selfloops, 1)
    net_degree = sum_dicts(in_degree, out_degree, 1)

    if total_degree:
        max_size = max(total_degree.values())
        min_size = min(total_degree.values())

        max_col = max(net_degree.values())
        min_col = min(net_degree.values())
    
    else:
        max_size = min_size = None
        max_col = min_col = None

    return total_degree, net_degree, max_size, min_size, max_col, min_col

def top_degree(G, in_out):
    if in_out == 'in':
        deg = dict(G.in_degree(weight='count'))
    elif in_out == 'out':
        deg = dict(G.out_degree(weight='count'))
    
    top = sorted(A, key=A.get, reverse=True)[:5]
    print(f"Top 5 by {in_out} = {top}")

def network_data(files, include=None, exclude=None, group=None):

    _, sources_df = load_files(files)
    data = get_full_data(files, include=include, exclude=exclude, from_to_flag=True)

    if not group:
        cols = ["from_index", "to_index"]
        grouped = data.groupby(cols, dropna=False).agg({'count': 'sum'}).reset_index()

        G = nx.from_pandas_edgelist(grouped, cols[0], cols[1], "count",
                                    create_using=nx.DiGraph())

        total_degree, net_degree, max_size, min_size, max_col, min_col = node_size_col(G)

        nodes = [dict(
                    data=dict(id=str(n), label=sources_df.loc[n, 'text'], 
                                size=total_degree[int(n)],
                                color=net_degree[int(n)]), 
                    selectable=True,
                    )
                for n in G.nodes]

    else:
        cols = sorted([col for col in data.columns if group in col])

        grouped = data.groupby(cols, dropna=False).agg({'count': 'sum'}).reset_index()

        G = nx.from_pandas_edgelist(grouped, cols[0], cols[1], "count",
                                    create_using=nx.DiGraph())

        total_degree, net_degree, max_size, min_size, max_col, min_col = node_size_col(G)

        nodes = [dict(
                    data=dict(id=str(n), label=str(n),
                              size=total_degree[n],
                              color=net_degree[n]),
                    selectable=True,
                    )
                for n in G.nodes]

    edges = [dict(
                data=dict(source=str(e[0]), target=str(e[1]), 
                label='', count=e[2]['count'])
            ) for e in G.edges.data()]

    sizecol = dict(min_col=min_col, max_col=max_col, 
                    min_size=min_size, max_size=max_size)

    G_dict = nx.to_dict_of_dicts(G)

    return nodes, edges, sizecol, G_dict

def gen_network(nodes, edges, sizecol, layout = 'concentric'):
    elements = nodes + edges
    if None in sizecol.values():
        print(sizecol)
        network = html.Div(dbc.Alert("The filter selection made returned a network with no links. "
                            "Please verify your filters or the chosen dataset!",
                            color="danger"), style={'padding':'80px', 'text-align':'center'})
    else:
        network = cyto.Cytoscape(
                    id='network-layout',
                    elements=elements,
                    style={'width': '100%', 'height': '800px'},
                    layout={
                        'name': layout,
                        'fit': True,
                        'animate': False,
                        'gravity': 10,
                        'nodeOverlap': 5e5,
                        'nodeRepulsion': 1e6,
                    },
                    stylesheet=gen_stylesheet(sizecol)
                )

    return network

def gen_stylesheet(sizecol, to_fade=None):

    target_edge_color = 'rgb(0, 150, 200)'
    source_edge_color = 'rgb(200, 0, 0)'
    edge_opacity = '0.5'

    edge_color_faded = 'rgb(70, 70, 70)'
    edge_opacity_faded = '0.8'

    node_color = 'rgb(0, 100, 150)'
    node_opacity = '0.7'

    node_color_selected = 'rgb(200, 90, 40)'
    node_opacity_faded = '0.2'
    
    min_col = sizecol['min_col']
    max_col = sizecol['max_col']

    min_size = sizecol['min_size']
    max_size = sizecol['max_size']

    mapcolor = (f"mapData(color," 
                f"{min_col}, {max_col}," 
                f"{source_edge_color}, {target_edge_color})")
    mapsize = f"mapData(size, {min_size}, {max_size}, 10, 60)"

    ss = [
            {
                'selector': 'edge',
                'style': {
                    'mid-target-arrow-color': source_edge_color,
                    'mid-target-arrow-shape': 'triangle',
                    'mid-target-arrow-fill': 'filled',

                    'curve-style': 'bezier',
                    'line-fill' : 'linear-gradient',
                    'line-gradient-stop-colors': [source_edge_color, target_edge_color],
                    'opacity' : edge_opacity,
                    # 'control-point-distances' : np.random.randint(low=-200, high=200, size=len(G.edges))
                }
            },

            {
                'selector': 'node',
                'style': {
                    'background-color': mapcolor,
                    'opacity':node_opacity,
                    'content': 'data(label)',
                    "width": mapsize,
                    "height": mapsize
                }
            }
        ]
    return ss


if __name__ == "__main__":
    files = {'edgelist': 'data/edgelist_202009.pkl',
             'sources': 'data/processed_sources_emm.pkl'}
    network_plots(files, group = 'lang')
    # get_full_data(files, from_to_flag = True)
