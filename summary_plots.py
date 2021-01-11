
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
    cols = ['category', 'region', 'country', 'lang']
    options = {}
    for col in cols:
        res = sorted(list(set(summary.loc[:, col]
                                .dropna(axis=0).values)))
        options[col] = [dict(label = r, value = r) for r in res]

    options['language'] = options.pop('lang')
    include_options = exclude_options = options

    if selections:
        pass

    return include_options, exclude_options
    

def get_full_data(files, include=None, exclude=None, from_to_flag = False):
    edge_df, sources_df = load_files(files)
    edge_df['count'] = 1

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

    if include and any(include):
        to_include = {cols[i]:v for i, v in enumerate(include) if v != None}
        if from_to_flag:
            from_dict = {f"from_{c}": v for c, v in to_include.items()}
            to_dict = {f"to_{c}": v for c, v in to_include.items()}
            from_dict.update(to_dict)
            to_include = from_dict

        submerged = []
        for col, values in to_include.items():
            submerged.append(merged[merged.loc[:,col].isin(values)])

        merged = pd.concat(submerged).drop_duplicates()

    if exclude and any(exclude):
        to_exclude = {cols[i]: v for i, v in enumerate(exclude) if v != None}
        # print("Exclude :", exclude, to_exclude)
        # if from_to_flag:
        #     from_dict = {f"from_{c}": v for c, v in to_exclude.items()}
        #     to_dict = {f"to_{c}": v for c, v in to_exclude.items()}
        #     from_dict.update(to_dict)
        #     to_exclude = from_dict
        submerged = []
        for col, values in to_exclude.items():
            if from_to_flag:
                col = [pre+col for pre in ['from_', 'to_']]
            else:
                col = [col]

            for c in col:
                merged = merged[~merged.loc[:, c].isin(values)]

            # submerged.append(merged[~merged.loc[:, col].isin(values)])

        # merged = pd.concat(submerged)
        # merged = merged[merged.duplicated(keep='first')]

    return merged
    

def summary_figs(files, include, exclude):

    merged = get_full_data(files, include, exclude)

    if merged.empty:
        return None

    figs = []

    cols = ['category', 'region', 'country', 'lang']
    grouped = merged.copy().groupby(cols, dropna=False).agg({'count': 'sum'}).reset_index()

    data = grouped.sort_values(['count','country'], ascending=[0,1]).to_dict('records')
    columns = [{"name": i, "id": i, } for i in (grouped.columns)]
    
    summary_table = dt.DataTable(
                        data=data, 
                        columns=columns,
                        filter_action="native",
                        sort_action="native",
                        row_selectable="multi",
                        selected_rows=[],
                        style_table={
                            'height': '500px',
                            'overflowY': 'auto',
                            'overflowX': 'auto',
                            'maxWidth': '100%'
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

    figs += [summary_table] + daily_articles(merged)

    return figs


def daily_articles(grouped):

    cols = ['region', 'lang', 'country']
    grouped = grouped.groupby(["parsed_date", "from_index"]+cols, 
                                dropna=False).agg({'count': 'sum'}).reset_index()

    by_day = grouped.groupby('parsed_date')['count'].sum()

    # grouped = pd.merge(grouped, by_day, on='parsed_date', how='left', suffixes=['', '_norm'])
    # grouped['count_norm'] = grouped['count']*100/grouped['count_norm']
    # max_count = grouped.groupby('from_index').sum()['count'].nlargest()
    # print(max_count)
    # print(sources_df.iloc[max_count.index,:])

    by_day_prop = by_day.cumsum()/sum(by_day)
    mid_date = by_day_prop[by_day_prop <= 0.5].idxmax()

    lower_date = mid_date - timedelta(days=7)
    upper_date = mid_date + timedelta(days=7)  

    figs = []

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
                formatted_name = name.ljust(15)
            areas[ordered_col[name]] = (go.Scatter(name=formatted_name, x=group['parsed_date'], y=group['count'],
                                            mode='lines', stackgroup='one',  hoveron='points'))
       
        title_dict = dict(region = 'Region', lang='Language', country='Country')
        titletext = f"Daily Article Count by {title_dict[col]}"

        fig = go.Figure(data=areas)
        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(
            template='simple_white',
            showlegend=True,
            # title=titletext,
            xaxis = dict(
                type='date',
                range=[lower_date, upper_date]),
            yaxis=dict(
                type='linear',
                ticksuffix=''),
            margin=dict(pad=5, b=0))
        
        figs.append(fig)
        # fig.show()

    return figs   

if __name__ == "__main__":
    files = {'edgelist': 'data/edgelist_202009.pkl',
            'sources': 'data/processed_sources_emm.pkl'}
    get_filter_options(files)
