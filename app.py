from dash import Dash, html, dcc
import plotly.graph_objects as go

# 3 stations:
STATIONS = [
    "Anand Vihar, New Delhi - DPCC",
    "R K Puram, Delhi - DPCC",
    "Punjabi Bagh, Delhi - DPCC",
]

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

        html.Label("Select a station:"),
        dcc.Dropdown(
            id="station-dropdown",
            options=[{"label": s, "value": s} for s in STATIONS],
            value=STATIONS[0],   # default selection
        ),

        dcc.Graph(id="forecast-chart", figure=placeholder_fig),
    ],
)

#run:
if __name__ == "__main__":
    app.run(debug=True)
