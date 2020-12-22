from datetime import datetime
from typing import List
import numpy as np
import pytz
from dateutil.relativedelta import relativedelta
from pandas import DataFrame
import plotly.express as px
import plotly.graph_objects as go
from Trips import Trips


def unix_time_millis(dt):
    return int(dt.timestamp())


def get_marks_from_start_end(start, end):
    nb_marks = 5
    result = []
    time_delta = int((end - start).total_seconds() / nb_marks)
    current = start
    if time_delta > 0:
        while current <= end:
            result.append(current)
            current += relativedelta(seconds=time_delta)
        result[-1] = end
        if time_delta < 3600 * 24:
            if time_delta > 3600:
                date_f = '%y-%m-%d %Hh'
            else:
                date_f = '%y-%m-%d %Hh%M'
        else:
            date_f = '%Y-%m'
        marks = {}
        for date in result:
            marks[unix_time_millis(date)] = str(date.strftime(date_f))
        return marks


def convert_datetime(st):
    return datetime.strptime(st.decode("utf-8"), "%Y-%m-%d %H:%M:%S+00:00").replace(tzinfo=pytz.UTC)


consumption_fig = None
consumption_df = None
trips_map = None
consumption_fig_by_speed = None


def get_figures(trips: List[Trips]):
    global consumption_fig, consumption_df, trips_map, consumption_fig_by_speed
    lats = []
    lons = []
    names = []
    for trip in trips:
        for points in trip.positions:
            lats = np.append(lats, points.longitude)
            lons = np.append(lons, points.latitude)
            names = np.append(names, [str(trip.start_at)])
        lats = np.append(lats, None)
        lons = np.append(lons, None)
        names = np.append(names, None)

    trips_map = px.line_mapbox(lat=lats, lon=lons, hover_name=names,
                               mapbox_style="stamen-terrain", zoom=12)
    consumption_df = DataFrame.from_records([tr.get_consumption() for tr in trips])
    consumption_fig = px.line(consumption_df, x="date", y="consumption", title='Consumption of the car')

    consum_df_by_speed = DataFrame.from_records(
        [{"speed": tr.speed_average, "value": tr.consumption_km} for tr in trips])
    consumption_fig_by_speed = px.histogram(consum_df_by_speed, x="speed", y="value", histfunc="avg",
                                            title="Consumption by speed")
    consumption_fig_by_speed.update_traces(xbins_size=15)
    consumption_fig_by_speed.update_layout(bargap=0.1)
    consumption_fig_by_speed.add_trace(
        go.Scatter(mode="markers", x=consum_df_by_speed["speed"], y=consum_df_by_speed["value"],
                   name="Trips"))
    consumption_fig_by_speed.update_layout(xaxis_title="average Speed km/h", yaxis_title="Consumption kW/100Km")


