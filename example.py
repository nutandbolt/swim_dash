import requests
import pandas as pd
import plotly.express as px

# get some lap timing data
df = pd.concat([
        pd.json_normalize(requests.get(f"https://ergast.com/api/f1/2021/7/laps/{l}.json").json()
                          ["MRData"]["RaceTable"]["Races"][0]["Laps"][0]["Timings"]
        ).assign(lap=l)
        for l in range(1, 25)
    ]).reset_index(drop=True)
# convert to timedelta...
df["time"] = (
    df["time"]
    .str.extract(r"(?P<minute>[0-9]+):(?P<sec>[0-9]+).(?P<milli>[0-9]+)")
    .apply(
        lambda r: pd.Timestamp(year=1970,month=1,day=1,
                               minute=int(r.minute),second=int(r.sec),microsecond=int(r.milli) * 10 ** 3,
        ),
        axis=1,
    )
    - pd.to_datetime("1-jan-1970").replace(hour=0, minute=0, second=0, microsecond=0)
)

# utility build display string from nanoseconds
def strfdelta(t, fmt="{minutes:02d}:{seconds:02d}.{milli:03d}"):
    d = {}
    d["minutes"], rem = divmod(t, 10 ** 9 * 60)
    d["seconds"], d["milli"] = divmod(rem, 10 ** 9)
    d["milli"] = d["milli"] // 10**6
    return fmt.format(**d)


# build a figure with lap times data...  NB use of hover_name for formatted time
fig = px.scatter(
    df,
    x="lap",
    y="time",
    color="driverId",
    hover_name=pd.Series(df["time"].values.astype(int)).apply(strfdelta),
    hover_data={"time":False},
    size=df.groupby("lap")["time"].transform(
        lambda s: s.rank(ascending=True).eq(1).values.astype(int)
    ),
)
# make figure more interesting... add best/worst and mean lap times...
fig.add_traces(
    px.line(
        df.groupby("lap")
        .agg(
            avg=("time", lambda s: s.mean()),
            min=("time", lambda s: s.min()),
            max=("time", lambda s: s.max()),
        )
        .reset_index(),
        x="lap",
        y=["avg", "min", "max"],
    ).data
)

# fix up tick labels
ticks = pd.Series(range(df["time"].values.astype('int64').min() - 10 ** 10, df["time"].values.astype('int64').max(), 10 ** 10,))
fig.update_layout(
    yaxis={
        "range": [
            df["time"].values.astype('int64').min() - 10 ** 10,
            df["time"].values.astype('int64').max(),
        ],
        "tickmode": "array",
        "tickvals": ticks,
        # "ticktext": ticks.apply(strfdelta)
    }
)
fig.show()

