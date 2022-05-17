# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# -m streamlit.cli run
# https://stackoverflow.com/questions/68146256/convert-times-to-designated-time-format-and-apply-to-y-axis-of-plotly-graph
import pandas as pd
import streamlit as st
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dateutil.parser as dparser
import datetime
from halloffame import hall_of_fame
from trendline import fit_trendline
from plot_metric import plot_metric
from config import mapping


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
    time_col = []
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
            if mapping[option]['plot'] == 'distance':
                fmt = mapping[option]['fmt']
                try:
                    input_df[[col+'_time', col+'_text', col+'_blank']] = \
                        input_df[col].str.split(r'[{(\[})\]]', expand=True)
                    input_df[col+'_time'] = input_df[col+'_time'].apply(lambda x: x.strip())
                except ValueError:
                    input_df[col+'_time'] = input_df[col]

                yaxis = [strptime(str(time), fmt) for time in input_df[col+'_time']]
                yaxis_time = [pd.Timestamp(year=1970, month=1, day=1, hour=int(time.hour), minute=int(time.minute),
                                           second=int(time.second),
                                           microsecond=int(time.microsecond)) - pd.to_datetime("1-jan-1970").replace
                              (hour=0, minute=0, second=0, microsecond=0) if time is not None else None for time in
                              yaxis]
                input_df[col] = yaxis_time
                rank = np.zeros(len(input_df[col]))
                i = 1
                for index in input_df[col].sort_values().index:
                    rank[index] = i
                    i += 1

                fig.add_trace(
                    go.Bar(name=str(date.date()), x=input_df['NAME'], y=input_df.iloc[:, time_column_index + 1],
                           customdata=pd.Series(input_df[col].values.astype('int64')).apply(strfdelta,
                           args=(mapping[option]['display_fmt'],)),
                           texttemplate="%{customdata} - %{y}M",
                           # text=pd.Series(input_df[col].values.astype('int64')).apply(strfdelta,
                           # args=(mapping[option]['display_fmt'],)),
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

                )
            else:
                fmt = mapping[option]['fmt']
                try:
                    input_df[[col+'_time', col+'_text', col+'_blank']] = \
                        input_df[col].str.split(r'[{(\[})\]]', expand=True)
                    input_df[col + '_time'] = input_df[col+'_time'].fillna('None')
                    input_df[col+'_time'] = input_df[col+'_time'].apply(lambda x: x.strip())
                    cus_data = input_df[col+'_text']
                    cus_data = cus_data.replace(np.nan, ' ')
                except ValueError:
                    input_df[col+'_time'] = input_df[col]
                    cus_data = [' ']*len(input_df[col])
                yaxis = [strptime(str(time), fmt) for time in input_df[col+'_time']]
                yaxis_time = [pd.Timestamp(year=1970, month=1, day=1, hour=int(time.hour), minute=int(time.minute),
                                           second=int(time.second),
                                           microsecond=int(time.microsecond)) - pd.to_datetime("1-jan-1970").replace
                              (hour=0, minute=0, second=0, microsecond=0) if time is not None else None for time in
                              yaxis]
                input_df[col] = yaxis_time
                rank = np.zeros(len(input_df[col]))
                i = 1
                for index in input_df[col].sort_values().index:
                    rank[index] = i
                    i += 1
                fig.add_trace(go.Bar(name=str(date.date()), x=input_df['NAME'], y=input_df[col],
                                     customdata=rank,
                                     text=cus_data,
                                     textposition="inside",
                                     hovertext=pd.Series(input_df[col].values.astype('int64')).apply(strfdelta,
                                     args=(mapping[option]['display_fmt'],)),
                                     hovertemplate='<b>%{x}</b><br>' + '%{hovertext}<br>'+'%{text}<br>'
                                                   + '<b>Rank</b> = %{customdata}<br>'
                                     ))

    if mapping[option]['plot'] == 'time':
        ticks = pd.Series(range((input_df.iloc[:, time_col].min()).view('int64').min()
                                - 10 ** 10,
                                input_df.iloc[:, time_col].values.astype('int64').max()
                                + 10 ** 10,  3*(10 ** 10)))
        fig.update_layout(
            showlegend=True,
            title_text=f'<b> {option}   </b>',
            title_font_color="black",
            width=1000,
            height=600,
            yaxis={
                "title": f"Time [{mapping[option]['yaxis_label']}]",
                "range": [(input_df.iloc[:, time_col].min()).view('int64').min() - 10 ** 10,
                          input_df.iloc[:, time_col].values.astype('int64').max() + (10 ** 10)],
                "tickmode": "array",
                "tickvals": ticks,
                "ticktext": ticks.apply(strfdelta, args=(mapping[option]['display_fmt'],))
            })
    fig.update_layout(barmode='group')
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True
    # fig.show()
    st.plotly_chart(fig)


def plot_athlete(athlete, data_range):
    # # sheet_id = "1Sjy1nZ5pHgoayKb32b--74Mgtag_qewB5EF4trRKFPY"
    # sheet_id = "19dCvddKN-oeLdg-qb-p8SY1iqS2WxUJKJHCwomvJK5A"
    # sheet_name = mapping[option]['url']
    #
    # url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    # input_df = pd.read_csv(url).dropna(axis=1, how="all")
    # fig = go.Figure()
    fig2 = make_subplots(rows=4, cols=2, start_cell="top-left", subplot_titles=WORKOUTS,
                         horizontal_spacing=0.15, vertical_spacing=0.1)
    i = 1
    j = 1
    for workout in WORKOUTS:

        sheet_name = mapping[workout]['url']
        header_row = mapping[workout]['header']
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        df = pd.read_csv(url).dropna(axis=1, how="all")
        if 'NAME ' in df.columns:
            df.rename(columns={'NAME ': 'NAME'}, inplace=True)
        df_athlete = df.loc[df['NAME'] == athlete, :].reset_index(drop=True)
        if data_range != 'All':
            df_athlete.dropna(axis=1, inplace=True)
            df_athlete = df_athlete.iloc[:, -8:]
        x_vals = []
        y_vals = []
        time_col = []
        for col in df_athlete.columns:
            try:
                temp = col.split(' ')[0]
                # distance = col.split(' ')[1]
                date = dparser.parse(temp, dayfirst=True, fuzzy=False)
            except (ValueError, IndexError):
                pass
            else:
                x_vals.append(date)

                time_column_index = df_athlete.columns.get_loc(col)
                time_col.append(time_column_index)

                fmt = mapping[workout]['fmt']
                yaxis = [strptime(str(time), fmt) for time in df_athlete[col]]
                yaxis_time = [pd.Timestamp(year=1970, month=1, day=1, hour=int(time.hour), minute=int(time.minute),
                                           second=int(time.second), microsecond=int(time.microsecond))
                              - pd.to_datetime("1-jan-1970").replace(hour=0, minute=0, second=0, microsecond=0)
                              if time is not None else None for time in yaxis]
                df_athlete.loc[:, col] = yaxis_time[0]
                # df_athlete.at[0, col] = yaxis_time[0]

                if yaxis_time[0] is None:
                    pass

                elif mapping[workout]['plot'] == 'distance':
                    y_vals.append(df_athlete.iloc[:, time_column_index + 1].values)
                    fig2.add_trace(
                        go.Bar(name=str(date.date()), x=[str(date.strftime("%d %b %y"))],
                               y=df_athlete.iloc[:, time_column_index + 1],
                               text=pd.Series(df_athlete[col].values.astype('int64')).apply(strfdelta,
                               args=(mapping[workout]['display_fmt'],)),
                               textposition='auto',
                               hovertext=pd.Series(df_athlete[col].values.astype('int64')).apply(strfdelta,
                               args=(mapping[workout]['display_fmt'],))),
                        row=i, col=j)
                    # help_fig = px.scatter(x=[str(date.strftime("%d %b %y"))],
                    #                       y=df_athlete.iloc[:, time_column_index + 1], trendline="ols")
                    # x_trend = help_fig["data"][0]['x']
                    # y_trend = help_fig["data"][0]['y']
                    #
                    # fig2.add_trace(
                    #     go.Scatter(x=x_trend, y=y_trend, name='trend'),
                    #     row=i, col=j)

                    fig2.update_yaxes(

                        title=f"Distance [M]",
                        fixedrange=True,
                        row=i, col=j
                    )
                    fig2.update_xaxes(
                        fixedrange=True,
                        row=i, col=j
                    )
                    # fig2.update_xaxes(type='category')

                elif mapping[workout]['plot'] == 'time':
                    y_vals.append(df_athlete[col].values[0])
                    fig2.add_trace(go.Bar(name=str(date.date()), x=[str(date.strftime("%d %b %y"))], y=df_athlete[col],
                                          text=pd.Series(df_athlete[col].values.astype('int64')).apply(strfdelta,
                                          args=(mapping[workout]['display_fmt'],)),
                                          textposition='auto',
                                          hovertemplate='<b>%{x}</b><br>'+'%{text}<br>'), row=i, col=j)

        try:
            ticks = pd.Series(range(df_athlete.iloc[:, time_col].fillna(np.nan).dropna(axis=1).values.astype('int64')
                                    .min() - 5 * (10 ** 10), df_athlete.iloc[:, time_col].dropna(axis=1).
                                    values.astype('int64').max() + 5 * (10 ** 10), 4 * (10 ** 10)))
        except ValueError:
            ticks = pd.Series(range(0, 5*(10**10), 10**10))

        if mapping[workout]['plot'] == 'time':
            # col_values = list(df_athlete.iloc[:, time_col].fillna(np.nan).dropna(axis=1).values.astype('int64'))
            col_values = pd.to_timedelta(df_athlete.iloc[:, time_col].values[0]).seconds*1e9
            # col_names = pd.to_datetime(df_athlete.iloc[:, time_col].fillna(np.nan).dropna(axis=1).columns.values,
            #                            dayfirst=
            #                            True)
            col_names = pd.to_datetime(x_vals, dayfirst=True)
            df = pd.DataFrame({'time_stamp': col_names, 'values': col_values})
            if not df['values'].isna().all():
                df_trend, slope = fit_trendline(df)
                if workout == 'Time Trial 100 M':
                    avg_tt_time = df['values'].iloc[-4:].mean()/1e9
                if workout == 'Swim Broken 1000 M':
                    avg_endurance_time = df['values'].iloc[-4:].mean()/1e9/10
                if workout == 'Pull Set 700 M':
                    avg_pull_time = df['values'].iloc[-4:].mean()/1e9/7
                if workout == 'Kick Set 100 M':
                    avg_kick_time = df['values'].iloc[-4:].mean()/1e9

                fig2.add_trace(go.Scatter(x=df_trend['time_stamp'].dt.strftime("%d %b %y"),
                                          y=df_trend['bestfit'],
                                          mode='lines + text',
                                          name='Trend line',
                                          text=['             ' + str(slope) + ' s'],
                                          textposition="top right",
                                          textfont=dict(
                                              family="sans serif",
                                              size=18,
                                              color="LightSeaGreen"
                                          ),
                                          line=dict(color='firebrick', width=1),
                                          hovertemplate=f'{str(slope)} s<br>',
                                          ), row=i, col=j)
            try:
                fig2.update_yaxes(

                    range=[df_athlete.iloc[:, time_col].fillna(np.nan).dropna(axis=1).values.astype('int64').min()
                           - 5 * (10 ** 10),
                           df_athlete.iloc[:, time_col].fillna(np.nan).dropna(axis=1).values.astype('int64').max()
                           + 5 * (10 ** 10)],
                    title=f"Time [{mapping[workout]['yaxis_label']}]",
                    tickmode="array",
                    tickvals=ticks,
                    ticktext=ticks.apply(strfdelta, args=(mapping[workout]['display_fmt'],)),
                    fixedrange=True,
                    row=i, col=j
                )
            except ValueError:
                fig2.update_yaxes(title=f"Time [{mapping[workout]['yaxis_label']}]")

            fig2.update_xaxes(
                fixedrange=True,
                row=i, col=j
            )

        j += 1
        if j > 2:
            j = 1
            i += 1

    CD = 1.07  # https://swimmingtechnology.com/measurement-of-the-active-drag-coefficient/
    A = 0.0736  # https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3590858/#FD5
    try:
        endurance_score = round(100 - (avg_endurance_time - avg_tt_time)/avg_tt_time * 100, 1)
    except NameError:
        endurance_score = 0
    try:
        lbody_pos_score = round(100 - (avg_endurance_time - avg_pull_time)/avg_pull_time * 100, 1)
        if lbody_pos_score > 100:
            lbody_pos_score = 100
    except NameError:
        lbody_pos_score = 0
    try:
        kick_score = round(100 - (avg_kick_time - avg_tt_time)/avg_tt_time*100, 1)
    except NameError:
        kick_score = 0
    try:
        pull_score = round(0.5*1000*CD*A*(100/avg_pull_time)**3, 1)  # In Watts
    except NameError:
        pull_score = 0
    total_score = round(endurance_score + pull_score + lbody_pos_score + kick_score, 1)
    fig2.update_layout(
        height=1150, width=1000,
        showlegend=False,
        title_text=f'<b> SWIM DATA FOR  {athlete}</b>',
        title_font_color="black",
    )
    score = [endurance_score, lbody_pos_score, kick_score, pull_score]
    colors = ['khaki', 'firebrick', 'blue', 'green']
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=['Endurance Score', 'LB pos Score', 'Kick Score', 'Pull Score'], y=score,
                          text=[endurance_score, lbody_pos_score, kick_score, str(pull_score)+' W'],
                          textposition='auto',
                          marker_color=colors))
    fig3.update_yaxes(range=[-20, 100], fixedrange=True)
    fig3.update_layout(
        height=600, width=600,
        showlegend=False,
        title_text=f'<b> SWIM SCORE FOR  {athlete} = {total_score}</b>',
    )
    fig3.update_yaxes(title='<b> SWIM SCORE <b>',
                      fixedrange=True)
    fig3.update_xaxes(fixedrange=True)

    # fig2.show()
    st.plotly_chart(fig2)
    st.plotly_chart(fig3)


WORKOUTS = ['Pull Set 400 M', 'Pull Set 700 M', 'Endurance 500 M', 'Kick Set 100 M', 'Time Trial 100 M',
            'Continuous Swim', 'Sprint 50 M', 'Swim Broken 1000 M']
ATHLETES = ['AJAY', 'ANURADHA', 'ASHWIN', 'ARUN B', 'DHRITHI', 'DIVYA N', 'MEGHANA', 'PRASHANTH', 'PRADEEP', 'RAHUL',
            'NIKHIL', 'PHANI', 'PRERANA', 'SHREYA', 'SRAVAN', 'NIKHIL(OG)']

ATHLETES.sort()

st.title("SWIM FOR FITNESS DASHBOARD")
display_mode = st.selectbox('Select Display Mode', ('Individual', 'Group', 'Swim Metric'))
hf_df = hall_of_fame(WORKOUTS).reset_index(drop=True)
# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

st.sidebar.image(r'./images/halloffame.gif')
st.sidebar.table(hf_df)
st.markdown(f'''
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 30rem;}}
        section[data-testid="stSidebar"] .css-1d391kg {{width: 30rem;}}
    </style>
''', unsafe_allow_html=True)

# name = st.selectbox('Select Athlete', ATHLETES)
# plot_athlete(name)
#
# option = st.selectbox('Select workout', WORKOUTS)
# plot_workout(option)

if display_mode == 'Individual':
    name = st.selectbox('Select Athlete', ATHLETES)
    data_select = st.radio('Data Range', ('All', 'Last 8 instances'))
    plot_athlete(name, data_select)
elif display_mode == 'Group':
    option = st.selectbox('Select workout', WORKOUTS)
    plot_workout(option)
elif display_mode == 'Swim Metric':
    plot_metric()
