# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# -m streamlit.cli run
# https://stackoverflow.com/questions/68146256/convert-times-to-designated-time-format-and-apply-to-y-axis-of-plotly-graph
import pandas as pd
import streamlit as st
import csv
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dateutil.parser as dparser
import datetime
import requests


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
    'Kick Set 200 M': {
        'url': "Kick%20Broken",
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


def plot_workout(option):
    # sheet_id = "1_Q7C3w_aCh9NErtnxLkDl1JYFlisPnDit09LvdcsLYg"#"19dCvddKN-oeLdg-qb-p8SY1iqS2WxUJKJHCwomvJK5A"
    sheet_name = mapping[option]['url']
    header_rows = mapping[option]['header']

    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    input_df = pd.read_csv(url).dropna(axis=1, how="all")
    if 'NAME ' in input_df.columns:
        input_df.rename(columns={'NAME ': 'NAME'}, inplace=True)
    col_names = pd.read_csv(url).head(0)
    fig = go.Figure()
    for col in input_df.columns:

        try:
            temp = col.split(' ')[0]
            # distance = col.split(' ')[1]
            date = dparser.parse(temp, dayfirst=True, fuzzy=True)
        except (ValueError, IndexError):
            pass

        else:
            time_column_index = input_df.columns.get_loc(col)

            if mapping[option]['plot'] == 'distance':
                fmt = mapping[option]['fmt']
                yaxis = [strptime(str(time), fmt) for time in input_df[col]]
                yaxis_time = [pd.Timestamp(year=1970, month=1, day=1, hour=int(time.hour), minute=int(time.minute),
                                           second=int(time.second),
                                           microsecond=int(time.microsecond)) - pd.to_datetime("1-jan-1970").replace
                              (hour=0, minute=0, second=0, microsecond=0) if time is not None else None for time in
                              yaxis]
                input_df[col] = yaxis_time
                fig.add_trace(
                    go.Bar(name=str(date.date()), x=input_df['NAME'], y=input_df.iloc[:, time_column_index + 1],
                           text=pd.Series(input_df[col].values.astype('int64')).apply(strfdelta,
                           args=(mapping[option]['display_fmt'],)),
                           textposition='auto',
                           hovertext=pd.Series(input_df[col].values.astype('int64')).apply(strfdelta,
                           args=(mapping[option]['display_fmt'],)),
                           ))
                fig.update_layout(
                    showlegend=True,
                    title_text=f'<b> {option}   </b>',
                    title_font_color="black",
                    yaxis={
                        "title": f"Distance [M]",
                    }
                    # font=dict(
                    #     family="Courier New, monospace",
                    #     size=18,
                    #     color="RebeccaPurple"
                    # )
                )
            else:
                fmt = mapping[option]['fmt']
                yaxis = [strptime(str(time), fmt) for time in input_df[col]]
                yaxis_time = [pd.Timestamp(year=1970, month=1, day=1, hour=int(time.hour), minute=int(time.minute),
                                           second=int(time.second),
                                           microsecond=int(time.microsecond)) - pd.to_datetime("1-jan-1970").replace
                              (hour=0, minute=0, second=0, microsecond=0) if time is not None else None for time in
                              yaxis]
                input_df[col] = yaxis_time
                fig.add_trace(go.Bar(name=str(date.date()), x=input_df['NAME'], y=input_df[col],
                                     hovertext=pd.Series(input_df[col].values.astype('int64')).apply(strfdelta,
                                     args=(mapping[option]['display_fmt'],)),

                                     ))

                # ticks = pd.Series(range(input_df[col].dropna().values.astype('int64').min() - 10 ** 10,
                #                         input_df[col].dropna().values.astype('int64').max() + 10 ** 10, 10 ** 10))
                ticks = pd.Series(range(input_df[col].dropna().values.astype('int64').min() - 10 ** 10,
                                        input_df[col].dropna().values.astype('int64').max()
                                        + 3 * (10 ** 10), 2*(10 ** 10)))
                fig.update_layout(
                    showlegend=True,
                    title_text=f'<b> {option}   </b>',
                    title_font_color="black",
                    width=1000,
                    height=600,
                    yaxis={
                        "title": f"Time [{mapping[option]['yaxis_label']}]",

                        "range": [input_df[col].dropna().values.astype('int64').min() - 10 ** 10,
                                  input_df[col].dropna().values.astype('int64').max() + 3 * (10 ** 10)],
                        "tickmode": "array",
                        "tickvals": ticks,
                        "ticktext": ticks.apply(strfdelta, args=(mapping[option]['display_fmt'],))
                    },
                    # font=dict(
                    #     family="Courier New, monospace",
                    #     size=18,
                    #     color="RebeccaPurple"
                    # )
                )

    fig.update_layout(barmode='group')
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    # fig.show()
    st.plotly_chart(fig)


def plot_athlete(athlete):
    # # sheet_id = "1Sjy1nZ5pHgoayKb32b--74Mgtag_qewB5EF4trRKFPY"
    # sheet_id = "19dCvddKN-oeLdg-qb-p8SY1iqS2WxUJKJHCwomvJK5A"
    # sheet_name = mapping[option]['url']
    #
    # url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    # input_df = pd.read_csv(url).dropna(axis=1, how="all")
    # fig = go.Figure()
    fig2 = make_subplots(rows=4, cols=2, start_cell="top-left", subplot_titles=WORKOUTS, horizontal_spacing=0.15)
    i = 1
    j = 1
    for workout in WORKOUTS:

        sheet_name = mapping[workout]['url']
        header_row = mapping[workout]['header']
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df = pd.read_csv(url).dropna(axis=1, how="all")
        if 'NAME ' in df.columns:
            df.rename(columns={'NAME ': 'NAME'}, inplace=True)
        df_athlete = df.loc[df['NAME'] == athlete, :]
        x_vals = []
        y_vals = []
        for col in df_athlete.columns:
            try:
                temp = col.split(' ')[0]
                # distance = col.split(' ')[1]
                date = dparser.parse(temp, dayfirst=True, fuzzy=True)
            except (ValueError, IndexError):
                pass
            else:
                # x_vals.append(date)
                # y_vals.append(df_athlete[col].values)
                time_column_index = df_athlete.columns.get_loc(col)
                fmt = mapping[workout]['fmt']
                yaxis = [strptime(str(time), fmt) for time in df_athlete[col]]
                yaxis_time = [pd.Timestamp(year=1970, month=1, day=1, hour=int(time.hour), minute=int(time.minute),
                                           second=int(time.second), microsecond=int(time.microsecond))
                              - pd.to_datetime("1-jan-1970").replace(hour=0, minute=0, second=0, microsecond=0)
                              if time is not None else None for time in yaxis]
                df_athlete.loc[:, col] = yaxis_time

                if yaxis_time[0] is None:
                    pass

                elif mapping[workout]['plot'] == 'distance':
                    fig2.add_trace(
                        go.Bar(name=str(date.date()), x=[str(date.strftime("%d %b %y"))],
                               y=df_athlete.iloc[:, time_column_index + 1],
                               text=pd.Series(df_athlete[col].values.astype('int64')).apply(strfdelta,
                               args=(mapping[workout]['display_fmt'],)),
                               textposition='auto',
                               hovertext=pd.Series(df_athlete[col].values.astype('int64')).apply(strfdelta,
                               args=(mapping[workout]['display_fmt'],))),
                        row=i, col=j)

                    fig2.update_yaxes(

                        title=f"Distance [M]",
                        row=i, col=j
                    )
                    fig2.update_xaxes(type='category')

                elif mapping[workout]['plot'] == 'time':

                    ticks = pd.Series(range(df_athlete[col].dropna().values.astype('int64').min() - 10 ** 10,
                                            df_athlete[col].dropna().values.astype('int64').max()
                                            + 3 * (10 ** 10), 10 ** 10))
                    fig2.add_trace(go.Bar(name=str(date.date()), x=[str(date.strftime("%d %b %y"))], y=df_athlete[col],
                                          text=pd.Series(df_athlete[col].values.astype('int64')).apply(strfdelta,
                                          args=(mapping[workout]['display_fmt'],)),
                                          textposition='auto',
                                          hovertext=pd.Series(df_athlete[col].values.astype('int64')).
                                          apply(strfdelta, args=(mapping[workout]['display_fmt'],))), row=i, col=j)
                    fig2.update_yaxes(

                        range=[df_athlete[col].dropna().values.astype('int64').min() - 10 ** 10,
                               df_athlete[col].dropna().values.astype('int64').max() + 3 * (10 ** 10)],
                        title=f"Time [{mapping[workout]['yaxis_label']}]",
                        tickmode="array",
                        tickvals=ticks,
                        ticktext=ticks.apply(strfdelta, args=(mapping[workout]['display_fmt'],)),
                        row=i, col=j
                    )
                    fig2.update_xaxes(type='category')

        j += 1
        if j > 2:
            j = 1
            i += 1

    fig2.update_layout(
        height=600, width=1000,
        showlegend=False,
        title_text=f'<b> SWIM DATA FOR  {athlete}</b>',
        title_font_color="black",
    )
    fig2.layout.xaxis.fixedrange = True
    fig2.layout.yaxis.fixedrange = True

    # fig2.show()
    st.plotly_chart(fig2)


WORKOUTS = ['Pull Set 400 M', 'Endurance 500 M', 'Kick Set 200 M', 'Time Trial 100 M', 'Continuous Swim', 'Sprint 50 M',
            'Swim Broken 1000 M']
ATHLETES = ['AJAY', 'ASHWIN', 'ARUN B', 'DIVYA N', 'MEGHANA', 'TEJAS', 'PRASHANTH', 'PRADEEP', 'MUKUND', 'MAHATHI',
            'RAHUL']


st.title("SWIM FOR FITNESS DASHBOARD")
display_mode = st.selectbox('Select Display Mode', ('Individual', 'Group'))

if display_mode == 'Individual':
    athlete = st.selectbox('Select Athlete', ATHLETES)
    plot_athlete(athlete)
else:
    option = st.selectbox('Select workout', WORKOUTS)
    plot_workout(option)
# plot_workout(WORKOUTS[0])
# plot_athlete(ATHLETES[0])
