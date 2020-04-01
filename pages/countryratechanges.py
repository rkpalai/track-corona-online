import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dateutil.parser import parse

from app import app

confirm_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"

death_url = ""

covid_time_conf = pd.read_csv(confirm_url)

covid_time_conf.drop(columns=["Lat", "Long", "Province/State"], axis=1, inplace=True)

columns = list(covid_time_conf.columns)  # .remove('Country/Region')

columns.remove("Country/Region")

columns = [parse(x) for x in columns]


col = [str(x.day) + " " + "(" + x.strftime("%b") + ")" for x in columns]

cols = ["Country"] + col

col_for_graph = columns

covid_time_conf.columns = cols

confirmed_cases = covid_time_conf.groupby("Country").sum()

confirmed_delta = confirmed_cases.diff(axis=1)

confirmed_delta.columns = col_for_graph

confirmed_delta = confirmed_delta.fillna(0)


layout = html.Div(
    [
        html.Div(
            [html.H2("Number of Cases (Increase/Decrease) Per Day")],
            style={"textAlign": "center", "padding-bottom": "30"},
        ),
        html.Div(
            [
                html.Span(
                    "Country: ",
                    className="six columns",
                    style={"text-align": "right", "width": "40%", "padding-top": 10},
                ),
                dcc.Dropdown(
                    id="country-selected",
                    value="India",
                    options=[
                        {"label": i, "value": i} for i in confirmed_cases.index.unique()
                    ],
                    placeholder="Filter by Country...",
                    style={
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto",
                        "width": "70%",
                    },
                    className="six columns",
                ),
            ],
            className="row",
        ),
        dcc.Graph(id="country-rate-growth-graph", config={"responsive": True}),
    ],
    className="container",
)


@app.callback(
    dash.dependencies.Output("country-rate-growth-graph", "figure"),
    [dash.dependencies.Input("country-selected", "value")],
)
def update_figure(selected):

    xaxis = confirmed_delta[confirmed_delta.index == selected].columns
    yaxis = confirmed_delta[confirmed_delta.index == selected].sum()

    trace = go.Scatter(x=xaxis, y=yaxis, mode="lines+markers", marker_color="hotpink")
    return {
        "data": [trace],
        "layout": go.Layout(
            xaxis=dict(
                tickangle=75,
                title_text="Date",
                title_font={"size": 20, "family": "Courier New"},
            ),
            yaxis=dict(
                title_text="No. of Cases per Day",
                title_font={"size": 20, "family": "Courier New"},
            ),
        ),
    }
