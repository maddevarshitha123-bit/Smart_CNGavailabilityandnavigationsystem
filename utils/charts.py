"""Plotly charts for analytics (built from the historical CSV + metrics.json)."""
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import DATA_PATH, METRICS_PATH

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def load_history():
    return pd.read_csv(DATA_PATH)


def wait_by_hour(df):
    d = df.groupby("hour", as_index=False)["waiting_time"].mean()
    return px.line(d, x="hour", y="waiting_time", markers=True,
                   title="Average waiting time by hour", labels={"waiting_time": "Minutes"})

def queue_by_station(df):
    d = df.groupby("station_id", as_index=False)["queue_length"].mean()
    d["station_id"] = d["station_id"].astype(str)
    return px.bar(d, x="station_id", y="queue_length", title="Average queue length by station")

def availability_distribution(df):
    d = df["availability"].value_counts().reset_index()
    d.columns = ["availability", "count"]
    return px.pie(d, names="availability", values="count", title="Availability distribution",
                  color="availability", color_discrete_map={"High": "#2e9e5b", "Medium": "#f0a500", "Low": "#d64545"})

def traffic_vs_wait(df):
    return px.box(df, x="traffic_level", y="waiting_time",
                  category_orders={"traffic_level": ["Low", "Medium", "High"]},
                  title="Traffic level vs waiting time")

def daily_demand(df):
    d = df.groupby("day_of_week", as_index=False)["vehicles_per_hour"].mean()
    d["day"] = d["day_of_week"].map(lambda i: DAYS[i])
    return px.bar(d, x="day", y="vehicles_per_hour", title="Average demand (vehicles/hour) by day of week")

def model_performance():
    """Bar chart of classifier accuracy/F1 from metrics.json (None if not trained yet)."""
    if not METRICS_PATH.exists():
        return None
    m = json.loads(METRICS_PATH.read_text())["classification"]
    fig = go.Figure()
    for metric in ("accuracy", "f1"):
        fig.add_bar(name=metric, x=list(m), y=[m[k][metric] for k in m])
    fig.update_layout(title="Classifier performance (on synthetic test data)", barmode="group")
    return fig

def load_metrics():
    return json.loads(METRICS_PATH.read_text()) if METRICS_PATH.exists() else None
