# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# -m streamlit.cli run
# https://stackoverflow.com/questions/68146256/convert-times-to-designated-time-format-and-apply-to-y-axis-of-plotly-graph
import pandas as pd
import streamlit as st
# import dateparser
import numpy as np
import csv
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dateutil.parser as dparser
import datetime
from config import mapping
import requests
# import plotly.io as pio
# pio.renderers.default = "browser"
sheet_id = '1MtzRZiacK93npe_i4AhJ5okC7RtKAo_3l2aWMdpHl7c'


def hall_of_fame(WORKOUTS, athlete=None):
    # utility build display string from nanoseconds
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
            time_var = datetime.datetime.strptime(str(s), time_fmt).time()
            time_stamp = pd.Timestamp(year=1970, month=1, day=1, hour=int(time_var.hour), minute=int(time_var.minute),
                                      second=int(time_var.second),
                                      microsecond=int(time_var.microsecond)) - pd.to_datetime("1-jan-1970").\
                replace(hour=0, minute=0, second=0, microsecond=0)

            return time_stamp
        except ValueError:
            return None

    def outer(date_format):
        def inner(cell):
            return strptime(cell, date_format)
        return inner

    hall_of_fame_df = pd.DataFrame(columns=['WORKOUT', 'NAME', 'TIME/DIST', 'DATE'])
    for workout in WORKOUTS:
        sheet_name = mapping[workout]['url']
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        input_df = pd.read_csv(url).dropna(axis=1, how="all")
        time_col = []
        if 'NAME ' in input_df.columns:
            input_df.rename(columns={'NAME ': 'NAME'}, inplace=True)

        for col in input_df.columns:

            try:
                temp = col.split(' ')[0]
                # distance = col.split(' ')[1]
                date = dparser.parse(temp, dayfirst=True, fuzzy=False)
            except (ValueError, IndexError):
                pass

            else:
                time_column_index = input_df.columns.get_loc(col)
                time_col.append(time_column_index)
                if mapping[workout]['plot'] == 'distance':
                    fmt = mapping[workout]['fmt']
                    try:
                        # input_df[[col + '_time', col + '_text', col + '_blank']] = \
                        #     input_df[col].str.split(r'[{(\[})\]]', expand=True)
                        input_df[col + '_time'] = \
                            input_df[col].str.split(r'[{(\[})\]]', expand=True)[0]

                        input_df[col + '_time'] = input_df[col + '_time'].apply(lambda x: x.strip())
                    except (ValueError, AttributeError):
                        input_df[col + '_time'] = input_df[col]
                else:
                    fmt = mapping[workout]['fmt']
                    try:
                        # input_df[[col+'_time', col+'_text', col+'_blank']] = \
                        #     input_df[col].str.split(r'[{(\[})\]]', expand=True)
                        input_df[col + '_time'] = \
                            input_df[col].str.split(r'[{(\[})\]]', expand=True)[0]

                        input_df[col + '_time'] = input_df[col+'_time'].fillna('None')
                        input_df[col+'_time'] = input_df[col+'_time'].apply(lambda x: x.strip())
                    except (ValueError, AttributeError):
                        input_df[col+'_time'] = input_df[col]

        fmt = mapping[workout]['fmt']
        if mapping[workout]['plot'] == 'distance':
            time_dist_col = []
            for col in time_col:
                time_dist_col.append(col)
                time_dist_col.append(col+1)
            rank_df = input_df.iloc[:, time_dist_col]
            rank_df = rank_df.set_index(input_df['NAME'])
            if athlete:
                rank_df = rank_df[rank_df.index == athlete]
            if rank_df.dropna().empty:
                temp_df = pd.DataFrame(columns=['WORKOUT', 'NAME', 'TIME/DIST', 'DATE'])
            else:
                dist_name = [col for col in rank_df.columns if 'DISTANCE' in col]
                rank_time_dist = rank_df.loc[:, dist_name].max().max()
                rank_names = list(rank_df[rank_df == rank_time_dist].dropna(how='all').index)
                find_date_frm_dist = rank_df[rank_df == rank_time_dist].dropna(axis=1, how='all').columns[0]
                date_col = rank_df.columns.get_loc(find_date_frm_dist)-1
                rank_date = str(dparser.parse(rank_df.columns[date_col].split(' ')[0], dayfirst=True, fuzzy=True).date())
                temp_df = pd.DataFrame({'NAME': rank_names, 'WORKOUT': workout,
                                        'TIME/DIST': rank_time_dist, 'DATE': rank_date})
        else:
            timings = [input_df.columns.get_loc(col) for col in input_df.columns if 'time' in col]
            input_df.drop(input_df.index[input_df['NAME'].isna()], inplace=True)
            rank_df = input_df.iloc[:, timings].applymap(func=outer(fmt)).copy()
            # rank_df = input_df.iloc[1::, timings].applymap(func=outer(fmt)).copy()
            # if athlete:
            rank_df = rank_df.set_index(input_df['NAME'])
            if athlete:
                rank_df = rank_df[rank_df.index == athlete]
            # else:
            #     rank_df = rank_df.set_index(input_df['NAME'][1::])
            rank_names = list(rank_df[rank_df == rank_df.min().min()].dropna(how='all').index)
        # if mapping[workout]['plot'] == 'distance':

            rank_time_dist = strfdelta(rank_df.min().min().value, mapping[workout]['display_fmt'])
            rank_date = list(rank_df[rank_df == rank_df.min().min()].dropna(axis=1, how='all').columns)
            rank_date = [str(dparser.parse(date.split(' ')[0], dayfirst=True, fuzzy=True).date()) for date in rank_date]
            try:
                temp_df = pd.DataFrame({'NAME': rank_names, 'WORKOUT': workout,
                                        'TIME/DIST': rank_time_dist, 'DATE': rank_date})
            except ValueError:
                # Same person getting same time on 2 different date scenario results in dataframe with 2 entries for
                # date while all other entries have length of 1
                temp_df = pd.DataFrame({'NAME': rank_names, 'WORKOUT': workout,
                                        'TIME/DIST': rank_time_dist, 'DATE': rank_date[-1]})

        hall_of_fame_df = pd.concat([hall_of_fame_df, temp_df])
    hall_of_fame_df['TIME/DIST'] = hall_of_fame_df['TIME/DIST'].astype('string')

    return hall_of_fame_df.copy()
