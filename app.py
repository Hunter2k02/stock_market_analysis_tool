from flask import Flask
from dash import Dash, html, dcc, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import requests
import pandas as pd
import pandas_ta as ta
import json




server = Flask(__name__)


with open("pairs.json", "r", encoding="utf-8") as f:
    list_of_currencies = json.load(f)
 


with open('grouped_indicators.json', 'r') as file:
    grouped_indicators = json.load(file)

indicator_list = [k for k in grouped_indicators.keys()]



app = Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',
    assets_folder='./assets/',
)



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
            html.H1("Crypto Dashboard" , className="title"),
            html.H3("Select a currency:", className="title2"),
            dcc.Dropdown(list_of_currencies, id ="coin-select", className="coin-select", value = "btcusd"),
            html.H3("Select first indicator:", className="title3"),
            dcc.Dropdown(indicator_list, id ="indicator-select", className="indicator-select", value = "rsi"),
            html.H3("Select second indicator:"),
            dcc.Dropdown(indicator_list, id ="indicator-select2", className="indicator-select2", value = "rsi"),
            html.H3("Click to draw line:"),
            html.Button('Draw', id='draw', className="draw"),
            
        ]),
])
                 
                          
        

@app.callback(
    
    Output('candles', 'figure'),
    Output('indicator', 'figure'),
    Output('indicator2', 'figure'),
    Output('volume', 'figure'),
    
    Input('coin-select', 'value'),
    Input('indicator-select', 'value'),
    Input('indicator-select2', 'value'),
    Input('interval', 'n_intervals'),
    
    
)

def update_graph(value, indicator1, indicator2, n_intervals):
    
    url = f"https://www.bitstamp.net/api/v2/ohlc/{value}/"
    
    params = {
        "step": 60,
        "limit": 60,
    }
    
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
        title=go.layout.Title(text=f"{value}")
    )
        
    )
    candles.update_layout(xaxis_rangeslider_visible=False, height=515, width=750)
    
    indicator = px.line(
        x=data.timestamp,
        y=data[indicator1],
        title=f"First indicator: {indicator1} Description",
        height=300,
        
        
    )
    indicator.update_layout(xaxis_rangeslider_visible=False, height=515, width=750)
    indicator.update_yaxes(title_text=None)  # Remove y-axis title
    indicator.update_xaxes(title_text=None)
    
    indicator2 = px.line(
        x=data.timestamp,
        y=data[indicator2],
        title=f"Second indicator: {indicator2}",
        height=300,
        
    )
    indicator2.update_layout(xaxis_rangeslider_visible=False, height=515, width=750)
    indicator2.update_yaxes(title_text=None)  # Remove y-axis title
    indicator2.update_xaxes(title_text=None)
    
    
    volume = px.bar(
        x=data.timestamp,
        y=data.volume,
        title="Volume",
        height=300,
    )
    volume.update_layout(xaxis_rangeslider_visible=False, height=515, width=750)
    volume.update_layout(autotypenumbers='convert types')
    volume.update_yaxes(title_text="Quantity")  # Update y-axis title to "Quantity"
    
    

    return candles, indicator, indicator2, volume



@server.route("/")
def hello():
    return app.index()



if __name__ == '__main__':
    server.run(debug=True)