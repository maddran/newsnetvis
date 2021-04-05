import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import datetime
import pandas as pd
import numpy as np
import io
import base64
from glob import glob

def parse_upload(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), 
                             sep='\t', index_col=None)
            if all(c in df.columns for c in ['from_index', 'to_index', 'parsed_date']):
                filetype = "edgelist"
            elif all(c in df.columns for c in ['country', 'lang', 'name', 'lat', 'lon']):
                filetype = "sources"
            else:
                filetype = None

            if filetype:
                saved_file = f"user_data/{filetype}.pkl"
                if filetype == "edgelist":
                    summarize(df).to_pickle(saved_file)
            else:
                saved_file = None

            return (filetype, df_table(df, filename), saved_file)
        else:
            raise(IOError)
            
    except Exception as e:
        print(e)
        return (None, [])
    

def parse_preload(click):

    edgelist_dict = {
                'sep': "data/edgelist_20200901.pkl",
                'nov' : "data/edgelist_202010.pkl"
    }
    
    fnames = [edgelist_dict[click], "data/processed_sources_emm.pkl"]

    data = [
            pd.read_pickle(fname)
            for fname in fnames
            ]

    return [(df_table(df, fnames[i]), fnames[i]) for i, df in enumerate(data)]

def df_table(df, filename):
    table_div = html.Div([
        html.H5(filename),

        dash_table.DataTable(
            data=df.head(100).to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            style_table={
                'height' : '300px',
                'overflowY': 'auto',
                'overflowX': 'auto',
                'maxWidth': '100%'
            }
        ),
        html.Hr(),  # horizontal line
    ])

    return table_div

def csv_to_pkl(files):
    for f in files:
        df = pd.read_csv(f, sep="\t", index_col=False)
        df.to_pickle(f"{f.split('.')[0]}.pkl")

def summarize(files, filters=None):
    dfs = []
    for ftype, fpath in files:
        dfs.append()
        df["parsed_date"] = pd.to_datetime(df["parsed_date"])
        df["count"] = 1
    # if filters:

    res = df.groupby(["from_index", "to_index"], dropna=False).agg(
        {'count': 'count'}).reset_index()
    return res


