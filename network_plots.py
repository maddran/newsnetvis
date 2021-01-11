import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt
import dash_cytoscape as cyto

import pandas as pd
import numpy as np
from datetime import timedelta

from summary_plots import get_full_data, load_files


def network_plots(files, include=None, exclude=None, group=None):

    _, sources_df = load_files(files)
    data = get_full_data(files, include=include, exclude=exclude, from_to_flag=True)

    # grouped = data.groupby(["from_index", "to_index"],
    #                           dropna=False).agg({'count': 'sum'}).reset_index()

    G = nx.DiGraph()
    if not group:
        G = nx.from_pandas_edgelist(grouped, "from_index", "to_index", "count")
        pos = get_pos(G)

        nodes = [dict(
                    data=dict(id=str(n), label=sources_df.loc[n, 'name']),
                    position=dict(x=pos[n][0], y=pos[n][1])
                ) for n in G.nodes]

    else:
        cols = sorted([col for col in data.columns if group in col])

        # for idx in ['from_index', 'to_index']:
        #     grouped = pd.merge(grouped, sources_df.loc[:, ['country']],
        #                     left_on=idx, right_index=True, how='left')
        #     grouped = grouped.rename(columns = {'country':f"{idx.split('_')[0]}_country"})

        grouped = data.groupby(cols, dropna=False).agg({'count': 'sum'}).reset_index()

        print("from", sorted(list(set(grouped[cols[0]]))))
        print("to", sorted(list(set(grouped[cols[1]]))))

        G = nx.from_pandas_edgelist(grouped, cols[0], cols[1], "count")
        pos = get_pos(G)

        nodes = [dict(
                    data=dict(id=str(n), label=str(n)),
                    position=dict(x=pos[n][0], y=pos[n][1])
                ) for n in G.nodes]


    edges = [dict(
                data=dict(source=str(e[0]), target=str(e[1]), label='')
            ) for e in G.edges]

    elements = nodes + edges

    network = cyto.Cytoscape(
                    id='cytoscape-layout-1',
                    elements=elements,
                    style={'width': '100%', 'height': '800px'},
                    layout={
                        'name': 'preset',
                        'fit' : False,
                        'animate' : False
                    },
                    stylesheet = gen_stylesheet(G)
                )

    return network

def scale(pos):
    keys, values = zip(*pos.items())
    x, y = zip(*values)

    # x*=100
    # y*=100

    scale = max(max(x)-min(x), max(y)-min(y))

    normed_x = x/scale
    normed_x = (normed_x - min(normed_x))*2000
    # normed_x /= 

    normed_y = y/scale
    normed_y = (normed_y - min(normed_y))*2000

    # min(normed_x)
    # normed_x += 500
    # normed_y += 300

    print(np.median(normed_x), np.median(normed_y))

    normed = list(zip(normed_x, normed_y))

    return dict(zip(keys, normed))

def get_pos(G):
    pos = nx.spring_layout(G)
    pos = scale(pos)
    return pos

def gen_stylesheet(G, selected_node = None):
    edge_color = 'rgb(70, 70, 70)'
    edge_opacity = '0.2'

    edge_color_selected = 'rgb(70, 70, 70)'
    edge_opacity_selected = '0.8'

    node_color = 'rgb(0, 57, 107)'
    node_opacity = '0.8'

    node_color_selected = 'rgb(200, 90, 40)'
    node_opacity_faded = '0.2'

    # if selected_node:


    ss = [
            {
                'selector': 'edge',
                'style': {
                    'mid-source-arrow-color': edge_color,
                    'mid-source-arrow-shape': 'triangle',
                    'mid-source-arrow-fill': 'filled',
                    'line-color': edge_color,
                    'opacity' : edge_opacity
                }
            },

            {
                'selector': 'node',
                'style': {
                    'background-color': node_color,
                    'opacity':node_opacity,
                    'content': 'data(label)'
                }
            }
        ]
    return ss


if __name__ == "__main__":
    files = {'edgelist': 'data/edgelist_202009.pkl',
             'sources': 'data/processed_sources_emm.pkl'}
    network_plots(files, group = 'lang')
    # get_full_data(files, from_to_flag = True)
