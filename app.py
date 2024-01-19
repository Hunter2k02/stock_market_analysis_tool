from flask import Flask
from dash import Dash, html, dcc, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import requests
import pandas as pd
import pandas_ta as ta
import json
from datetime import date, timedelta
from random import randint
from constants import API_KEY
import os 
import shutil
import io


def get_news():
    yesterday = date.today() - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    url = f"https://api.marketaux.com/v1/news/all?industries=Technology&filter_entities=true&limit=10&published_after={yesterday}T17:47&api_token={API_KEY}"

    response = requests.get(url)
    json_data = response.json()
    choice = randint(0, len(json_data["data"])-1)
    # Check if there is description, title or source
    if json_data["data"][choice]["description"] is None:
        json_data["data"][choice]["description"] = "No description available"

    elif json_data["data"][choice]["title"] is None:
        json_data["data"][choice]["title"] = "No title available"
        
    elif json_data["data"][choice]["source"] is None:
        json_data["data"][choice]["source"] = "No source available"
    
    return json_data, choice

json_data, choice = get_news()

server = Flask(__name__)

with open("pairs.json", "r") as f:
    list_of_currencies = json.load(f)
 
list_of_currencies = [c.upper() for c in list_of_currencies]

with open('grouped_indicators.json', 'r') as file:
    grouped_indicators = json.load(file)

time_dict = {
    'minute': 60,
    'hour': 3600,
    'day': 86400
}

indicator_list = [k.upper() for k in grouped_indicators.keys()]

app = Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',
    assets_folder='./assets/',
    update_title=None
)
app.title = "MyStock"

app.config.suppress_callback_exceptions = True

app.layout = html.Div(id='main', className="main-div", children=[
    html.Div(id='charts', className="charts", children=[
        dcc.Graph(id='candles', className="candles"),
        dcc.Graph(id='indicator', className="indicator"),
        dcc.Graph(id='volume',  className="volume"),
        dcc.Graph(id='indicator2', className="indicator2"),
        dcc.Interval(id='interval', interval=2000)
    ]), 
        
    html.Div(id='menu', className="menu-div", children=[
        html.H1("Dashboard" , className="title"),
        html.H3("Select a currency:", className="title2"),
        dcc.Dropdown(list_of_currencies, id ="coin-select", className="coin-select", value = "btcusd"),
        html.H3("Select first indicator:", className="title3"),
        dcc.Dropdown(indicator_list, id ="indicator-select", className="indicator-select", value = "rsi"),
        html.H3("Select second indicator:"),
        dcc.Dropdown(indicator_list, id ="indicator-select2", className="indicator-select2", value = "rsi"),
        html.H3("Select time interval:"),
        dcc.Dropdown([k for k in time_dict.keys()] ,id ="frequency-select3", className="frequency-select3", value = "day"),
        html.Div(id='news', className="news", children=[
            html.H4("News:", className="title4"),
            html.H5(f"{json_data['data'][choice]['title']}"),
            html.H5(f" {json_data['data'][choice]['description']}"),
            html.Plaintext(f"Source: {json_data['data'][choice]['source']}")
        ], style={'display': 'flex', 'font-family':'Roboto, sans-serif', "border": "1px solid black"}),
        html.Button("Download images", id="download", className="Button", n_clicks=0),
        dcc.Download(id="download-image")
    ])
], style={'display': 'flex', 'font-family':'Roboto, sans-serif'})
     
# Callback to download images 
@app.callback(
    Output("download-image", "data"),
    
    
    Input("download", "n_clicks"),
    prevent_initial_call=True,
)
# Function to download images
def downloader(n_clicks):
    """
    This function generates and saves images of candlestick charts, indicator charts, and volume chart.
    It then creates a zip file containing the images and returns it as a downloadable file.
    
    Parameters:
        n_clicks (int): The number of times the function has been clicked.
        
    Returns:
        dash.Dash.send_file: The downloadable zip file containing the generated images.
    """
    
    if not os.path.exists("images"):
        os.makedirs("images")
    candles.write_image("images/figure.png")
    indicator_chart.write_image("images/figure1.png")
    indicator_chart2.write_image("images/figure2.png")
    volume.write_image("images/figure3.png")
    
    shutil.make_archive("images", "zip", "images")
    
    return dcc.send_file("images.zip")
      
# Callback to update graphs           
@app.callback(
    Output('candles', 'figure'),
    Output('indicator', 'figure'),
    Output('indicator2', 'figure'),
    Output('volume', 'figure'),
    
    Input('coin-select', 'value'),
    Input('indicator-select', 'value'),
    Input('indicator-select2', 'value'),
    Input('frequency-select3', 'value'),
    Input('interval', 'n_intervals'),
)


# Function to update graphs
def update_graph(value, indicator1, indicator2, frequency,  n_intervals):
    """
    Update the graph with new data based on the given parameters.

    Parameters:
    - value (str): The value to analyze (e.g., stock symbol).
    - indicator1 (str): The first indicator to plot.
    - indicator2 (str): The second indicator to plot.
    - frequency (str): The frequency of the data (e.g., "hourly", "daily").
    - n_intervals (int): The number of intervals to update the graph.

    Returns:
    - candles (go.Figure): The candlestick chart.
    - indicator_chart (px.line): The chart for the first indicator.
    - indicator_chart2 (px.line): The chart for the second indicator.
    - volume (px.bar): The volume chart.
    """
    
    # Declare the global variables to be used in the function 'downloader'
    global candles, indicator_chart, indicator_chart2, volume
    
    # Construct the API URL
    url = f"https://www.bitstamp.net/api/v2/ohlc/{value.lower()}/"

    # Set the parameters for the API request
    params = {
        "step": time_dict[frequency],
        "limit": 60,
    }

    
    indicator1, indicator2 = indicator1.lower(), indicator2.lower()

    # Get the corresponding functions for the indicators
    function1, function2 = getattr(ta, indicator1), getattr(ta, indicator2)

    # Fetch the data from the API
    data = requests.get(url, params=params).json()["data"]["ohlc"]
    data = pd.DataFrame(data)
    

    # Convert the timestamp to datetime format
    data['timestamp'] = data['timestamp'].astype(int)
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s', errors='ignore')
    data["timestamp"] = data["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    # Prepare the keyword arguments for the indicators
    kwargs1 = {}
    kwargs2 = {}
    for i in grouped_indicators[indicator1]:
        kwargs1[i] = data[i].astype(float)
    for i in grouped_indicators[indicator2]:
        kwargs2[i] = data[i].astype(float)

    # Apply the indicators to the data
    data[indicator1] = function1(**kwargs1)
    data[indicator2] = function2(**kwargs2)

    # Drop rows with missing values
    data = data.dropna()

    # Create the candlestick chart
    candles = go.Figure(
        data=[
            go.Candlestick(
                x=data.timestamp,
                open=data.open,
                high=data.high,
                low=data.low,
                close=data.close,
            )
        ],
        layout=go.Layout(
            title=go.layout.Title(text=f"{value.upper()}"),
        )
    )
    candles.update_layout(
        xaxis_rangeslider_visible=False,
        xaxis_title="Date",
        yaxis_title="Price",
        plot_bgcolor="white",
        paper_bgcolor="whitesmoke"
    )
    candles.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Date"
    )
    candles.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Price"
    )

    # Create the chart for the first indicator
    indicator_chart = px.line(
        x=data.timestamp,
        y=data[indicator1],
        title=f"First indicator: {indicator1.upper()}",
    )
    indicator_chart.update_layout(
        xaxis_rangeslider_visible=False,
        plot_bgcolor="white",
        paper_bgcolor="whitesmoke"
    )
    indicator_chart.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Date"
    )
    indicator_chart.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Value"
    )
    indicator_chart.update_traces(line_color='red')

    # Create the chart for the second indicator
    indicator_chart2 = px.line(
        x=data.timestamp,
        y=data[indicator2],
        title=f"Second indicator: {indicator2.upper()}",
    )
    indicator_chart2.update_layout(
        xaxis_rangeslider_visible=False,
        plot_bgcolor="white",
        paper_bgcolor="whitesmoke"
    )
    indicator_chart2.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Date"
    )
    indicator_chart2.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Value"
    )
    indicator_chart2.update_traces(line_color='darkviolet')

    # Create the volume chart
    volume = px.bar(
        x=data.timestamp,
        y=data.volume,
        title="Volume",
    )
    volume.update_layout(
        xaxis_rangeslider_visible=False,
        autotypenumbers='convert types',
        plot_bgcolor="white",
        paper_bgcolor="whitesmoke"
    )
    volume.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Date"
    )
    volume.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Volume"
    )

    return candles, indicator_chart, indicator_chart2, volume

@server.route("/")
def index():
    return app.index()

if __name__ == '__main__':
    server.run(debug=True)