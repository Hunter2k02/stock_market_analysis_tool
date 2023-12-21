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

# Function to get news from MarketAux API

def get_news():
    yesterday = date.today() - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    url = f"https://api.marketaux.com/v1/news/all?industries=Technology&filter_entities=true&limit=10&published_after={yesterday}T17:47&api_token={API_KEY}"

    response = requests.get(url)
    json_data = response.json()
    choice = randint(0, len(json_data["data"])-1)
    if json_data["data"][choice]["description"] == None:
        json_data["data"][choice]["description"] = "No description available"

    elif json_data["data"][choice]["title"] == None:
        json_data["data"][choice]["title"] = "No title available"
        
    elif json_data["data"][choice]["source"] == None:
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

indicator_list = [k for k in grouped_indicators.keys()]
indicator_list = [i.upper() for i in indicator_list]

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
        ], style={'display': 'flex', 'font-family':'Roboto, sans-serif', "border": "1px solid black"})
    ])
], style={'display': 'flex', 'font-family':'Roboto, sans-serif'})
                 
                          
        

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

def update_graph(value, indicator1, indicator2, frequency,  n_intervals):
    
    url = f"https://www.bitstamp.net/api/v2/ohlc/{value.lower()}/"
    
    params = {
        "step": time_dict[frequency],
        "limit": 60,
    }
    indicator1 = indicator1.lower()
    indicator2 = indicator2.lower()

    function1 = getattr(ta, indicator1)
    function2 = getattr(ta, indicator2)
    
    
    data = requests.get(url, params=params).json()["data"]["ohlc"]
    data = pd.DataFrame(data)
    
    data['timestamp'] = data['timestamp'].astype(int)
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s', errors='ignore')

    data["timestamp"] = data["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    kwargs1 = {}
    kwargs2 = {}
    for i in grouped_indicators[indicator1]:
        kwargs1[i] = data[i].astype(float)
    for i in grouped_indicators[indicator2]:
        kwargs2[i] = data[i].astype(float)
        
    
    data[indicator1] = function1(**kwargs1)
    data[indicator2] = function2(**kwargs2)
    
    data = data.dropna()
   
    
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
        title=go.layout.Title(text=f"{value.upper()}",
        )
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
    
    

    indicator = px.line(
        x=data.timestamp,
        y=data[indicator1],
        title=f"First indicator: {indicator1.upper()}",
        
        
        
    )
    indicator.update_layout(
        xaxis_rangeslider_visible=False, 
        plot_bgcolor="white", 
        paper_bgcolor="whitesmoke"
        )
    indicator.update_xaxes(
    mirror=True,
    ticks='outside',
    showline=True,
    linecolor='black',
    gridcolor='lightgrey',
    title_text="Date"
    )
    indicator.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Value"
    )
    indicator.update_traces(line_color='red')
   
    indicator2 = px.line(
        x=data.timestamp,
        y=data[indicator2],
        title=f"Second indicator: {indicator2.upper()}",
       
        
    )
    indicator2.update_layout(
        xaxis_rangeslider_visible=False, 
        plot_bgcolor="white", 
        paper_bgcolor="whitesmoke"
    )
    
    indicator2.update_xaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Date"
    )

    indicator2.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=True,
        linecolor='black',
        gridcolor='lightgrey',
        title_text="Value"
    )
    indicator2.update_traces(line_color='darkviolet')
    
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
    return candles, indicator, indicator2, volume



@server.route("/")
def hello():
    return app.index()



if __name__ == '__main__':
    server.run(debug=True)