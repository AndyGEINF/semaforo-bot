import pytest
from src.indicators.technical_indicators import calculate_sma, calculate_ema
from src.indicators.market_metrics import get_market_cap

def test_calculate_sma():
    data = [1, 2, 3, 4, 5]
    period = 3
    expected_sma = 4.0
    assert calculate_sma(data, period) == expected_sma

def test_calculate_ema():
    data = [1, 2, 3, 4, 5]
    period = 3
    expected_ema = 4.0  # Adjust based on the actual EMA calculation
    assert calculate_ema(data, period) == expected_ema

def test_get_market_cap():
    price = 100
    circulating_supply = 1000
    expected_market_cap = 100000
    assert get_market_cap(price, circulating_supply) == expected_market_cap