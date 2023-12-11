import pandas_ta as ta
import inspect
import json

indicators_names = ['aberration', 'accbands', 'ad', 'adosc', 'adx', 'alma', 'amat', 'ao', 'aobv', 'apo', 'aroon', 'atr', 'bbands', 'bias', 'bop', 'brar', 'cci', 'cdl_pattern', 'cdl_z', 'cfo', 'cg', 'chop', 'cksp', 'cmf', 'cmo', 'coppock', 'cti', 'decay', 'decreasing', 'dema', 'donchian', 'dpo', 'ebsw', 'efi', 'ema', 'entropy', 'eom', 'er', 'eri', 'fisher', 'fwma', 'ha', 'hilo', 'hl2', 'hlc3', 'hma', 'hwc', 'ichimoku', 'increasing', 'inertia', 'jma', 'kama', 'kc', 'kdj', 'kst', 'kurtosis', 'kvo', 'linreg', 'log_return', 'long_run', 'macd', 'mad', 'massi', 'mcgd', 'median', 'mfi', 'midpoint', 'midprice', 'mom', 'natr', 'nvi', 'obv', 'ohlc4', 'pdist', 'percent_return', 'pgo', 'ppo', 'psar', 'psl', 'pvi', 'pvo', 'pvol', 'pvr', 'pvt', 'pwma', 'qqe', 'qstick', 'quantile', 'rma', 'roc', 'rsi', 'rsx', 'rvgi', 'rvi', 'short_run', 'sinwma', 'skew', 'slope', 'sma', 'smi', 'squeeze', 'squeeze_pro', 'ssf', 'stc', 'stdev', 'stoch', 'stochrsi', 'supertrend', 'swma', 't3', 'td_seq', 'tema', 'thermo', 'tos_stdevall', 'trima', 'trix', 'true_range', 'tsi', 'tsignals', 'ttm_trend', 'ui', 'uo', 'variance', 'vhf', 'vidya', 'vortex', 'vwap', 'vwma', 'wcp', 'willr', 'wma', 'xsignals', 'zlma', 'zscore']

required_args = ['open', 'high', 'low', 'close', 'volume']

grouped_indicators = {}

for indicator_name in indicators_names:
    indicator_func = getattr(ta, indicator_name)
    indicator_args = inspect.signature(indicator_func).parameters.keys()
    common_args = set(indicator_args) & set(required_args)
    grouped_indicators[indicator_name] = list(common_args)


with open('grouped_indicators.json', 'w') as file:
    json.dump(grouped_indicators, file)
