from flask import Flask, render_template, request, redirect, url_for, session
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import requests
import pandas as pd
import pandas_ta as ta
import json
import datetime as dt
server = Flask(__name__)

list_of_currencies = []
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
for i in range(len(data)):
    list_of_currencies.append(data[i]['currency'])    



app = Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/'
)

app.layout = html.Div([
        
        
        dcc.Dropdown(list_of_currencies, id ="coin-select", value = "BTC"),
        dcc.Graph(id='candles'),
        dcc.Graph(id='indicator'),
        
        
        dcc.Interval(id='interval', interval=2000),
    ])

@app.callback(
    Output('candles', 'figure'),
    Output('indicator', 'figure'),
    Input('interval', 'n_intervals'),
    
)
def update_graph(n_intervals):
    url = "https://www.bitstamp.net/api/v2/ohlc/btcusd/"
    
    params = {
        "step": 60,
        "limit": 44,
    }
    
    
    data = requests.get(url, params=params).json()["data"]["ohlc"]
    data = pd.DataFrame(data)
    data['timestamp'] = data['timestamp'].astype(int)
    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s', errors='ignore')

    data["timestamp"] = data["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    data["rsi"] = ta.rsi(data.close.astype(float))
    
    data = data.iloc[14:]
   
    
    candles = go.Figure(
        data=[
            go.Candlestick(
                x=data.timestamp,
                open=data.open,
                high=data.high,
                low=data.low,
                close=data.close,
            )
        ]
    )
    candles.update_layout(xaxis_rangeslider_visible=False, height = 400, width = 1000)
    
    indicator = px.line(
        x=data.timestamp,
        y=data.rsi,
        title="RSI",
        height=300,
        
    )
    indicator.update_layout(xaxis_rangeslider_visible=False, height = 400, width = 1000)
    

    

    return candles, indicator


@server.route("/")
def hello():
    return render_template('index.html')

@server.route("/dash")
def my_dash_app():
    return app.index()

if __name__ == '__main__':
    server.run(debug=True)