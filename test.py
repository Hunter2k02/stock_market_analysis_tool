import pandas as pd
import pandas_ta as ta
import requests
import json 



# with open('grouped_indicators.json', 'r') as file:
#     grouped_indicators = json.load(file)
    
# with open('fine_indicators.json', 'r') as file:
#     fine_indicators = json.load(file)



# counter = 0 
# results = {}
# faulty_indicators = []    

# for k in grouped_indicators.keys():
#     indicator1 = k
#     url = f"https://www.bitstamp.net/api/v2/ohlc/btcusd/"
        
#     params = {
#         "step": 60,
#         "limit": 60,
#     }

#     function1 = getattr(ta, indicator1)

#     data = requests.get(url, params=params).json()["data"]["ohlc"]
#     data = pd.DataFrame(data)

#     data['timestamp'] = data['timestamp'].astype(int)
#     data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s', errors='ignore')
#     data["timestamp"] = data["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

#     kwargs = {}
    
    
#     for i in grouped_indicators[indicator1]:
        
#         kwargs[i] = data[i].astype(float)

    
#     try:
#         data[indicator1] = function1(**kwargs)
#         data = data.dropna()
#         results[indicator1] = True
        
#     except Exception as e:
#         print(f"Error occurred: {e}")
#         faulty_indicators.append(indicator1)
        
#     print(f"Test case {counter}")
#     counter += 1

print(help(ta.sma))