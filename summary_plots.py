import pandas as pd
import numpy as np
from datetime import timedelta

import dash_table as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def load_files(files):
    for ftype, fpath in files.items():
        if ftype == 'edgelist':
            edge_df = pd.read_pickle(fpath)
            edge_df["parsed_date"] = pd.to_datetime(edge_df["parsed_date"])
        elif ftype == 'sources':
            sources_df = pd.read_pickle(fpath)

    return (edge_df, sources_df)


def get_filter_options(files, selections=None):
    summary = get_full_data(files)
    cols = ['category', 'region', 'country', 'lang', 'topic1']
    options = {}
    for col in cols:
        res = sorted(list(set(summary.loc[:, col]
                                .dropna(axis=0).values)))
        options[col] = [dict(label = r, value = r) for r in res]

    options['language'] = options.pop('lang')
    options['topic'] = options.pop('topic1')
    include_options = exclude_options = options

    if selections:
        pass

    return include_options, exclude_options
    
def get_topics(t1, t2):
    if not pd.isnull(t2):
        return '+'.join(sorted([t1, t2]))
    else:
        return t1

def get_full_data(files, include=None, exclude=None, from_to_flag = False):
    edge_df, sources_df = load_files(files)
    edge_df['count'] = 1
    edge_df['topic2'] = edge_df['topic2'].replace({np.nan: None})
    edge_df['topics'] = [get_topics(t1, t2) for t1, t2 in zip(edge_df.topic1, edge_df.topic2)]

    cols = ['category', 'region', 'country', 'lang']

    merged = edge_df

    if from_to_flag:
        temp_cols = []
        for idx in ['from_index', 'to_index']:
            merged = pd.merge(merged, sources_df.loc[:, cols],
                            left_on=idx, right_index=True, how='left')
            renamed = [f"{idx.split('_')[0]}_{c}" for c in cols]
            merged = merged.rename(columns = dict(zip(cols, renamed)))
            temp_cols+=renamed
                                      
    else:
        merged = pd.merge(merged, sources_df.loc[:, cols],
                        left_on='from_index', right_index=True, how='left')

    cols += ['topics']

    if include and any(include):
        to_include = {cols[i]:v for i, v in enumerate(include) if v and len(v)!=0}

        print(include)

        for col, values in to_include.items():
            if from_to_flag and col != 'topics':
                col = [pre+col for pre in ['from_', 'to_']]
            else:
                col = [col]

            if len(to_include)==1:
                for c in col:
                    if c != 'topics':
                        merged = merged[merged.loc[:, c].isin(values)]
                    else:
                        merged = merged[merged.loc[:, c].str.contains(
                                        '|'.join(values))]
                        
            else:
                submerged = []
                print(to_include)
                for c in col:
                    if c != 'topics':
                        submerged.append(merged[merged.loc[:, c].isin(values)])
                    else:
                        submerged.append(merged[merged.loc[:, c].str.contains(
                                        '|'.join(values))])

                merged = pd.concat(submerged).drop_duplicates()

    if exclude and any(exclude):
        to_exclude = {cols[i]: v for i, v in enumerate(exclude) if v and len(v)!=0}

        for col, values in to_exclude.items():
            if from_to_flag and col != 'topics':
                col = [pre+col for pre in ['from_', 'to_']]
            else:
                col = [col]

            for c in col:
                if c != 'topics':
                    merged = merged[~merged.loc[:, c].isin(values)]
                else:
                    merged = merged[~merged.loc[:, c].str.contains(
                                        '|'.join(values))]
    
    # print(set(merged.topics))

    return merged
    

def summary_figs(files, include, exclude):

    merged = get_full_data(files, include, exclude, True)
    n_sources = len(set(list(merged['from_index'].values)+
                        list(merged['to_index'].values)))

    if merged.empty:
        return None

    figs = []

    cols = ['category', 'region', 'country', 'lang']

    for prefix in ['from_', 'to_']:
        group_cols = [f'{prefix}{col}' for col in cols]
        grouped = merged.copy().groupby(group_cols, dropna=False).agg({'count': 'sum'}).reset_index()

        data = grouped.sort_values(['count', f'{prefix}country'], ascending=[0,1]).head(20).to_dict('records')
        columns = [{"name": i.split('_')[-1].upper(), "id": i, } for i in grouped.columns]
        
        summary_table = dt.DataTable(
                            data=data, 
                            columns=columns,
                            filter_action="native",
                            sort_action="native",
                            style_table={
                                # 'height': '500px',
                                'overflowY': 'auto',
                                'overflowX': 'auto',
                                'maxWidth': '95%'
                            }, 
                            style_as_list_view=True,
                            style_cell={
                                'padding': '5px',
                                'whiteSpace': 'normal',
                                'height': 'auto',
                                },
                            style_header={
                                    'backgroundColor': 'white',
                                    'fontWeight': 'bold'
                            })

        figs += [summary_table]

    figs += daily_articles(merged) + [n_sources]

    return figs


def daily_articles(grouped):

    figs = []

    cols = ['from_region', 'from_lang', 'from_country']
    grouped = grouped.groupby(["parsed_date", "from_index"]+cols, 
                                dropna=False).agg({'count': 'sum'}).reset_index()

    try:
        by_day = grouped.groupby('parsed_date')['count'].sum()

        by_day_prop = by_day.cumsum()/sum(by_day)
        mid_date = by_day_prop[by_day_prop <= 0.5].idxmax()
  
    except:
        mid_date = by_day_prop.index[0]

    lower_date = mid_date - timedelta(days=7)
    upper_date = mid_date + timedelta(days=7)


    for _, col in enumerate(cols):
        by_group = (grouped[grouped['parsed_date'].notna()]
                    .groupby(["parsed_date", col], dropna=False)
                    .agg({'count': 'sum'}).reset_index()
                    .groupby(col))
        ordered_col = (grouped[grouped['parsed_date'].notna()].groupby(col)
                        .agg({'count': 'sum'}).sort_values('count', ascending=True)
                        .index)
        ordered_col = {c:i for i,c in enumerate(list(ordered_col))}

        areas = ['']*len(ordered_col)
    
        for name, group in by_group:
            if len(name) > 15:
                formatted_name = name[0:15]+'...'
            else:
                formatted_name = name#.ljust(15)
            areas[ordered_col[name]] = (go.Scatter(name=formatted_name, x=group['parsed_date'], y=group['count'],
                                                   mode='lines', stackgroup='one',  hoveron='points', line_shape='spline'))
       

        fig = go.Figure(data=areas)
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(
            template='simple_white',
            # width=700,
            xaxis = dict(
                type='date',
                range=[lower_date, upper_date]),
            yaxis=dict(
                type='linear',
                ticksuffix=''),
            legend=dict(
                yanchor = 'top',
                xanchor = 'left',
                y = 1, x = 1.05),
            showlegend = True,
            margin=dict(pad=0, t=30, b=0))
        
        figs.append(fig)
        # fig.show()

    return figs   

if __name__ == "__main__":
    files = {'edgelist': 'data/edgelist_202009.pkl',
            'sources': 'data/processed_sources_emm.pkl'}
    get_filter_options(files)
