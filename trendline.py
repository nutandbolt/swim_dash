import pandas as pd
import plotly.graph_objects as go
import numpy as np
import datetime
import statsmodels.api as sm


def fit_trendline(df_in):
    df_in.dropna(inplace=True)
    df_in['serialtime'] = [(d - datetime.datetime(1970, 1, 1)).days for d in df_in['time_stamp']]
    df_in['serial'] = [i for i in range(1, len(df_in['serialtime']) + 1)]
    x = sm.add_constant(df_in['serial'])
    model = sm.OLS(df_in['values'], x).fit()
    df_in['bestfit'] = model.fittedvalues
    try:
        slope = round(model.params[1]/1e9, 1)
    except IndexError:
        slope = 0
    return df_in, slope


