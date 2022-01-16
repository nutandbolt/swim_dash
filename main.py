# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pandas as pd
import streamlit as st
import plotly
import plotly.graph_objects as go
import dateutil.parser as dparser

mapping = {
            'Pull Set': "Pull%20Broken",
            'Endurance': "Endurance",
            'Kick Set': "Kick%20Broken",
            'Time Trial': "Time%20Trial",
            'Continuous Swim': "Continuous%20Swim",
            'Swim Broken': "Swim%20Broken",
            'Sprint': "Others"
           }


option = st.selectbox('Select workout', ('Pull Set', 'Endurance', 'Kick Set', 'Time Trial', 'Continuous Swim',
                                         'Swim Broken', 'Sprint'))
sheet_name = mapping[option]
sheet_id = "1Sjy1nZ5pHgoayKb32b--74Mgtag_qewB5EF4trRKFPY"
sheet_id = "19dCvddKN-oeLdg-qb-p8SY1iqS2WxUJKJHCwomvJK5A"

url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
input_df = pd.read_csv(url).dropna(axis=1, how="all")

for col in input_df.columns:
    fig = go.Figure()
    try:
        date = dparser.parse(col, fuzzy=True)
    except ValueError:
        print(col)
        pass

    else:
        fig.add_trace(go.bar(name=date, x=input_df['NAME'], y=input[col]))

fig.update_layout(barmode='group')

st.plotly_chart(fig)

# print(test)

