import pandas as pd
import streamlit as st
import numpy as np
import csv
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dateutil.parser as dparser
import datetime
import requests


def strfdelta(t, fmt="{minutes:02d}:{seconds:02d}.{milli:03d}"):
    d = {}
    if "hours" in fmt:
        d["hours"], rem = divmod(t, 10 ** 9 * 60 * 60)
        d["minutes"], rem2 = divmod(rem, 10 ** 9 * 60)
        d["seconds"], d["milli"] = divmod(rem2, 10 ** 9)
        d["milli"] = d["milli"] // 10 ** 6
    else:
        d["minutes"], rem = divmod(t, 10 ** 9 * 60)
        d["seconds"], d["milli"] = divmod(rem, 10 ** 9)
        d["milli"] = d["milli"] // 10 ** 6

    return fmt.format(**d)


def strptime(s, time_fmt):
    try:
        return datetime.datetime.strptime(s, time_fmt).time()
    except ValueError:
        return None


sheet_id = '1qjes1n_ljhhFi1MFeMdpklHGmBqvKTkNBEMAi1B5XMo'
sheet_name = '200%20main%20k'
url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
input_df = pd.read_csv(url).dropna(axis=1, how="all")
fmt = "{minutes:02d}:{seconds:02d}.{milli:03d}"
time_fmt = "%M:%S"

if 'NAME ' in input_df.columns:
    input_df.rename(columns={'NAME ': 'NAME'}, inplace=True)
col_names = pd.read_csv(url).head(0)
fig = go.Figure()
time_col = []
for col in input_df.columns:

    try:
        temp = col.split(' ')[0]
        # distance = col.split(' ')[1]
        date = dparser.parse(temp, dayfirst=True, fuzzy=True)
    except (ValueError, IndexError):
        pass

    else:
        time_column_index = input_df.columns.get_loc(col)
        time_col.append(time_column_index)

        try:
            input_df[[col + '_time', col + '_text', col + '_blank']] = \
                input_df[col].str.split(r'[{(\[})\]]', expand=True)
            input_df[col + '_time'] = input_df[col + '_time'].fillna('None')
            input_df[col + '_time'] = input_df[col + '_time'].apply(lambda x: x.strip())
            cus_data = input_df[col + '_text']
        except ValueError:
            input_df[col + '_time'] = input_df[col]
            cus_data = []
        yaxis = [strptime(str(time), time_fmt) for time in input_df[col + '_time']]
        yaxis_time = [pd.Timestamp(year=1970, month=1, day=1, hour=int(time.hour), minute=int(time.minute),
                                   second=int(time.second),
                                   microsecond=int(time.microsecond)) - pd.to_datetime("1-jan-1970").replace
                      (hour=0, minute=0, second=0, microsecond=0) if time is not None else None for time in
                      yaxis]
        input_df[col] = yaxis_time
        hover_text = pd.Series(input_df[col].values.astype('int64')).apply(strfdelta, args=(fmt,))
        fig.add_trace(go.Bar(name=str(date.date()), x=input_df['NAME'], y=input_df[col],
                             customdata=hover_text,
                             text=cus_data,
                             textposition="inside",
                             hovertemplate='<b>%{x}</b><br>' + '%{customdata}<br>' + '%{text}<br>'))
ticks = pd.Series(range((input_df.iloc[:, time_col].min()).view('int64').min()
                        - 10 ** 10,
                        input_df.iloc[:, time_col].values.astype('int64').max()
                        + 10 ** 10, 10 ** 10))
fig.update_layout(
    showlegend=True,
    title_text='test',
    title_font_color="black",
    width=1000,
    height=600,
    yaxis={
        "title": "Time",
        "range": [(input_df.iloc[:, time_col].min()).view('int64').min() - 10 ** 10,
                  input_df.iloc[:, time_col].values.astype('int64').max() + (10 ** 10)],
        "tickmode": "array",
        "tickvals": ticks,
        "ticktext": ticks.apply(strfdelta, args=(fmt,))
    })
fig.update_layout(barmode='group')
fig.layout.xaxis.fixedrange = True
fig.layout.yaxis.fixedrange = True
fig.show()
