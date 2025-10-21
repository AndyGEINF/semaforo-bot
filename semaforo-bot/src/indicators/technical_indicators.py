from typing import List
import pandas as pd

def moving_average(data: pd.Series, window: int) -> pd.Series:
    return data.rolling(window=window).mean()

def exponential_moving_average(data: pd.Series, window: int) -> pd.Series:
    return data.ewm(span=window, adjust=False).mean()

def relative_strength_index(data: pd.Series, window: int) -> pd.Series:
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def bollinger_bands(data: pd.Series, window: int, num_std_dev: int) -> (pd.Series, pd.Series):
    ma = moving_average(data, window)
    std = data.rolling(window=window).std()
    upper_band = ma + (std * num_std_dev)
    lower_band = ma - (std * num_std_dev)
    return upper_band, lower_band

def macd(data: pd.Series, short_window: int = 12, long_window: int = 26, signal_window: int = 9) -> (pd.Series, pd.Series):
    short_ema = exponential_moving_average(data, short_window)
    long_ema = exponential_moving_average(data, long_window)
    macd_line = short_ema - long_ema
    signal_line = exponential_moving_average(macd_line, signal_window)
    return macd_line, signal_line

def stochastic_oscillator(data: pd.Series, window: int) -> pd.Series:
    lowest_low = data.rolling(window=window).min()
    highest_high = data.rolling(window=window).max()
    return 100 * ((data - lowest_low) / (highest_high - lowest_low))