import pandas as pd
import statistics as stat
import streamlit as st
import numpy as np
import csv
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import dateutil.parser as dparser
import datetime
from halloffame import hall_of_fame
from trendline import fit_trendline
import requests
# import plotly.io as pio
# pio.renderers.default = "browser"


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
        return datetime.datetime.strptime(s, time_fmt).time()
    except ValueError:
        return None


sheet_id = '1MtzRZiacK93npe_i4AhJ5okC7RtKAo_3l2aWMdpHl7c'

mapping = {
    'Pull Set 700 M': {
        'url': "Pull%20Broken_700M",
        'fmt': "%M:%S.%f",
        'display_fmt': "{minutes:02d}:{seconds:02d}.{milli:03d}",
        'plot': 'time',
        'yaxis_label': "MM:SS:sss",
        'header': 2
    },
    'Pull Set 400 M': {
        'url': "Pull%20Broken",
        'fmt': "%M:%S.%f",
        'display_fmt': "{minutes:02d}:{seconds:02d}.{milli:03d}",
        'plot': 'time',
        'yaxis_label': "MM:SS:sss",
        'header': 2
    },
    'Endurance 500 M': {
        'url': "Endurance",
        'fmt': "%M:%S.%f",
        'display_fmt': "{minutes:02d}:{seconds:02d}.{milli:03d}",
        'plot': 'time',
        'yaxis_label': "MM:SS:sss",
        'header': 1

    },
    'Kick Set 100 M': {
        'url': "Kick%20100M",
        'fmt': "%M:%S.%f",
        'display_fmt': "{minutes:02d}:{seconds:02d}.{milli:03d}",
        'plot': 'time',
        'yaxis_label': "MM:SS:sss",
        'header': 2

    },
    'Time Trial 100 M': {
        'url': "Time%20Trial",
        'fmt': "%M:%S.%f",
        'display_fmt': "{minutes:02d}:{seconds:02d}.{milli:03d}",
        'plot': 'time',
        'yaxis_label': "MM:SS:sss",
        'header': 2

    },
    'Continuous Swim': {
        'url': "Continuous%20Swim",
        'fmt': "%H:%M:%S",
        'display_fmt': "{hours:02d}:{minutes:02d}:{seconds:02d}.{milli:03d}",
        'plot': 'distance',
        'yaxis_label': "H:MM:SS",
        'header': 1
    },
    'Swim Broken 1000 M': {
        'url': "Swim%20Broken",
        'fmt': "%M:%S.%f",
        'display_fmt': "{minutes:02d}:{seconds:02d}.{milli:03d}",
        'plot': 'time',
        'yaxis_label': "MM:SS:sss",
        'header': 1

    },
    'Sprint 50 M': {
        'url': "Others",
        'fmt': "%M:%S.%f",
        'display_fmt': "{minutes:02d}:{seconds:02d}.{milli:03d}",
        'plot': 'time',
        'yaxis_label': "MM:SS:sss",
        'header': 1

    }
}


def plot_metric():

    WORKOUTS = ['Pull Set 700 M', 'Kick Set 100 M', 'Time Trial 100 M', 'Swim Broken 1000 M']
    ATHLETES = ['AJAY', 'ANURADHA', 'ASHWIN', 'ARUN B', 'DHRITHI', 'DIVYA N', 'MEGHANA', 'PRASHANTH', 'PRADEEP',
                'RAHUL', 'NIKHIL', 'PHANI', 'PRERANA', 'SHREYA', 'SRAVAN', 'NIKHIL(OG)']
    # sheet_id = "1_Q7C3w_aCh9NErtnxLkDl1JYFlisPnDit09LvdcsLYg"#"19dCvddKN-oeLdg-qb-p8SY1iqS2WxUJKJHCwomvJK5A"
    timing_dict = {}
    for workout in WORKOUTS:
        sheet_name = mapping[workout]['url']
        header_rows = mapping[workout]['header']

        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df = pd.read_csv(url).dropna(axis=1, how="all")

        if 'NAME ' in df.columns:
            df.rename(columns={'NAME ': 'NAME'}, inplace=True)

        for athlete in ATHLETES:
            try:
                dict_len = len(timing_dict[athlete])
            except KeyError:
                timing_dict.update({athlete: {}})

            df_athlete = df.loc[df['NAME'] == athlete, :].reset_index(drop=True).dropna(axis=1)
            df_athlete = df_athlete.loc[:, ~df_athlete.columns.isin(['Unnamed: 0', 'NAME'])]
            if df_athlete.empty:
                pass
            else:
                times = [datetime.datetime.strptime(s, "%M:%S.%f").time() for s in df_athlete.iloc[:, -4:].values.flatten()]
                time_stamp = [(pd.Timestamp(year=1970, month=1, day=1, hour=int(time.hour), minute=int(time.minute),
                              second=int(time.second), microsecond=int(time.microsecond))
                              - pd.to_datetime("1-jan-1970").replace(hour=0, minute=0, second=0, microsecond=0)).seconds
                              for time in times]
                if workout == 'Pull Set 700 M':
                    avg_time = stat.mean(time_stamp)/7
                    w_name = "avg_pull"
                elif workout == 'Time Trial 100 M':
                    avg_time = stat.mean(time_stamp)
                    w_name = "avg_tt"
                elif workout == 'Swim Broken 1000 M':
                    avg_time = stat.mean(time_stamp)/10
                    w_name = "avg_endurance"
                elif workout == 'Kick Set 100 M':
                    avg_time = stat.mean(time_stamp)
                    w_name = "avg_kick"

                timing_dict[athlete].update({w_name: avg_time})

    for athlete in ATHLETES:
        try:
            endurance_score = round(100 - (timing_dict[athlete]['avg_endurance']
                                           - timing_dict[athlete]['avg_tt']) / timing_dict[athlete]['avg_tt'] * 100,1)
        except (NameError, KeyError):
            endurance_score = 0
        timing_dict[athlete].update({'endurance_score': endurance_score})

        try:
            lbody_score = round(100 - (timing_dict[athlete]['avg_endurance']
                                       - timing_dict[athlete]['avg_pull']) / timing_dict[athlete]['avg_pull'] * 100, 1)
        except (NameError, KeyError):
            lbody_score = 0
        timing_dict[athlete].update({'lbody_score': lbody_score})

        try:
            kick_score = round(100 - (timing_dict[athlete]['avg_kick']
                                      - timing_dict[athlete]['avg_tt']) / timing_dict[athlete]['avg_tt'] * 100, 1)
        except (NameError, KeyError):
            kick_score = 0
        timing_dict[athlete].update({'kick_score': kick_score})

        try:
            CD = 1.07  # https://swimmingtechnology.com/measurement-of-the-active-drag-coefficient/
            A = 0.0736  # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3590858/#FD5
            pull_score = round(0.5*1000*CD*A*(100/timing_dict[athlete]['avg_pull'])**3, 1)
        except (NameError, KeyError):
            pull_score = 0
        timing_dict[athlete].update({'pull_score': pull_score})

        try:
            total_score = timing_dict[athlete]['kick_score'] + timing_dict[athlete]['pull_score'] + \
                          timing_dict[athlete]['lbody_score'] + timing_dict[athlete]['endurance_score']
        except (NameError, KeyError):
            total_score = 0

        timing_dict[athlete].update({'total_score': total_score})

    metric_df = pd.DataFrame.from_dict(timing_dict, orient='index')
    fig = make_subplots(
        rows=3, cols=2,
        specs=[[{}, {}],
               [{}, {}],
               [{"colspan": 2}, None]],
        subplot_titles=("PULL SCORE IN WATTS", "KICK SCORE", "ENDURANCE SCORE", "LBODY SCORE", "TOTAL SCORE"))
    metric_df = round(metric_df.sort_values(by='total_score', ascending=False), 1)
    pull_values = metric_df.pull_score
    kick_values = metric_df.kick_score
    endurance_values = metric_df.endurance_score
    lbody_values = metric_df.lbody_score
    total_values = metric_df.total_score

    fig.add_trace(go.Bar(x=pull_values.sort_values(ascending=False).index,
                         y=pull_values.sort_values(ascending=False),
                         name='PULL SCORE',
                         text=pull_values.sort_values(ascending=False),
                         textposition='auto',
                         marker_color=['orange']*len(pull_values)),
                  row=1, col=1)
    fig.add_trace(go.Bar(x=kick_values.sort_values(ascending=False).index,
                         y=kick_values.sort_values(ascending=False),
                         name='KICK SCORE',
                         text=kick_values.sort_values(ascending=False),
                         textposition='auto',
                         marker_color=['cyan']*len(kick_values)),
                  row=1, col=2)
    fig.add_trace(go.Bar(x=endurance_values.sort_values(ascending=False).index,
                         y=endurance_values.sort_values(ascending=False),
                         text=endurance_values.sort_values(ascending=False),
                         textposition='auto',
                         marker_color=['hotpink']*len(endurance_values)),
                  row=2, col=1)
    fig.add_trace(go.Bar(x=lbody_values.sort_values(ascending=False).index,
                         y=lbody_values.sort_values(ascending=False),
                         name='LBODY SCORE',
                         text=lbody_values.sort_values(ascending=False),
                         textposition='auto',
                         marker_color=['lightgreen']*len(lbody_values)),
                  row=2, col=2)

    fig.add_trace(go.Bar(x=total_values.index,
                         y=pull_values,
                         name='PULL SCORE'),
                  row=3, col=1)
    fig.add_trace(go.Bar(x=total_values.index,
                         y=kick_values,
                         name='KICK SCORE'),
                  row=3, col=1)
    fig.add_trace(go.Bar(x=total_values.index,
                         y=endurance_values,
                         name='ENDURANCE SCORE'),
                  row=3, col=1)
    fig.add_trace(go.Bar(x=total_values.index,
                         y=lbody_values,
                         name='LBODY SCORE',
                         text=total_values, textposition='auto'),
                  row=3, col=1)
    fig.update_layout(barmode='stack',)

    fig.update_layout(width=1000, height=800, showlegend=False, title_text="SWIM METRIC")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightPink', nticks=10, fixedrange=True)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightPink', fixedrange=True)
    fig.update_yaxes(range=[0, 50], row=1, col=1, fixedrange=True)
    st.plotly_chart(fig)
    st.image(r'./images/calc.jpg')

# if __name__ == 'main':
# plot_metric()
