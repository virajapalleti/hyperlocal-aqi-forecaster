from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd

from src.aqi_utils import pm25_to_category

#loading data
predictions = pd.read_csv("data/processed/dashboard_predictions.csv")
predictions["hour_utc"] = pd.to_datetime(predictions["hour_utc"], utc=True)

# Stations come from the data itself instead of a hardcoded lisyt now
STATIONS = sorted(predictions["location_name"].unique().tolist())
STATION_COORDS = {
    "Anand Vihar, New Delhi - DPCC": (28.6469, 77.3160),
    "R K Puram, Delhi - DPCC":       (28.5631, 77.1869),
    "Punjabi Bagh, Delhi - DPCC":    (28.6742, 77.1310),
}

def build_station_summary():
    rows = []
    for station in STATIONS:
        dff = predictions[predictions["location_name"] == station].sort_values("hour_utc")
        latest = round(dff["predicted_pm25"].max())
        category, color, _ = pm25_to_category(latest)
        lat, lon = STATION_COORDS[station]
        rows.append({"station": station, "lat": lat, "lon": lon,
                     "peak_pred": latest, "category": category, "color": color})
    return pd.DataFrame(rows)

station_summary = build_station_summary()

import plotly.express as px

def build_map_figure():
    fig = px.scatter_mapbox(
        station_summary,
        lat="lat", lon="lon",
        color="category",
        color_discrete_map=dict(zip(station_summary["category"], station_summary["color"])),
        hover_name="station",
        hover_data={"peak_pred": True, "category": True, "lat": False, "lon": False},
        size_max=20,
        zoom=10,
        height=450,
    )
    fig.update_traces(marker=dict(size=22, opacity=1.0))
    fig.update_layout(
        mapbox_style="open-street-map",   # free, no API key needed
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(title="AQI category"),
    )
    return fig

map_figure = build_map_figure()
# print(station_summary)

#creatign the app now, render will use exposed server later for deployment
app = Dash(__name__)
server = app.server

#empty charts
placeholder_fig = go.Figure()
placeholder_fig.update_layout(
    title="PM2.5 forecast will appear here",
    xaxis_title="Time",
    yaxis_title="PM2.5 (µg/m³)",
)


# layout:
app.layout = html.Div(
    style={"maxWidth": "900px", "margin": "0 auto", "fontFamily": "sans-serif"},
    children=[
        html.H1("Hyperlocal AQI Forecaster — Delhi"),
        html.P("24-hour PM2.5 forecast by monitoring station."),

        dcc.Graph(id="delhi-map", figure=map_figure),

        html.Hr(),

        html.Label("Select a station:"),
        dcc.Dropdown(
            id="station-dropdown",
            options=[{"label": s, "value": s} for s in STATIONS],
            value=STATIONS[0],   # default selection
        ),
        html.Div(id="health-alert", style={"margin": "16px 0", "padding": "16px","borderRadius": "8px", "color": "white"}),
    

        dcc.Graph(id="forecast-chart", figure=placeholder_fig),
    ],
)

# ---- CALLBACK: when station changes, redraw the chart ----
@app.callback(
    Output("forecast-chart", "figure"),
    Output("health-alert", "children"),
    Output("health-alert", "style"),
    Input("station-dropdown", "value"),
)
def update_chart(selected_station):
    dff = predictions[predictions["location_name"] == selected_station].sort_values("hour_utc")

    # ---- chart (same as before) ----
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dff["hour_utc"], y=dff["actual_pm25"],
                             mode="lines", name="Actual PM2.5", line=dict(color="black")))
    fig.add_trace(go.Scatter(x=dff["hour_utc"], y=dff["predicted_pm25"],
                             mode="lines", name="Predicted PM2.5", line=dict(color="royalblue")))
    fig.update_layout(title=f"24h-ahead PM2.5 — {selected_station}",
                      xaxis_title="Time (UTC)", yaxis_title="PM2.5 (µg/m³)",
                      legend=dict(orientation="h", y=1.1))

    # ---- health alert ----
    latest_pred = round(dff["predicted_pm25"].iloc[-1])
    latest_time = dff["hour_utc"].iloc[-1]
    category, color, message = pm25_to_category(latest_pred)

    # Worst (highest) predicted value across the test window
    peak_pred = dff["predicted_pm25"].max()
    peak_category, _, _ = pm25_to_category(peak_pred)

    alert_text = html.Div([
        html.Strong(f"Forecast for {latest_time:%d %b %Y %H:%M} UTC: "
                    f"{latest_pred:.0f} µg/m³ — {category}"),
        html.Br(),
        html.Span(message),
        html.Br(),
        html.Small(f"Peak forecast in test window: {peak_pred:.0f} µg/m³ — {peak_category}",
                   style={"opacity": 0.85}),
    ])

    alert_style = {"margin": "16px 0", "padding": "16px",
                   "borderRadius": "8px", "color": "white",
                   "backgroundColor": color}

    return fig, alert_text, alert_style

#run:
if __name__ == "__main__":
    app.run(debug=True)
