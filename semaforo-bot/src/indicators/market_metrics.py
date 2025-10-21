from typing import List, Dict

def get_market_metrics(data: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Calculate market metrics from the provided market data.

    Parameters:
    - data: A list of dictionaries containing market data with keys like 'price', 'volume', etc.

    Returns:
    A dictionary containing calculated market metrics such as 'average_price', 'total_volume', etc.
    """
    if not data:
        return {}

    total_price = sum(item['price'] for item in data)
    total_volume = sum(item['volume'] for item in data)
    average_price = total_price / len(data)

    metrics = {
        'average_price': average_price,
        'total_volume': total_volume,
    }

    return metrics

def calculate_price_change(current_price: float, previous_price: float) -> float:
    """
    Calculate the percentage change in price.

    Parameters:
    - current_price: The current price of the asset.
    - previous_price: The previous price of the asset.

    Returns:
    The percentage change in price.
    """
    if previous_price == 0:
        return 0.0
    return ((current_price - previous_price) / previous_price) * 100

def get_market_trend(data: List[Dict[str, float]]) -> str:
    """
    Determine the market trend based on the provided market data.

    Parameters:
    - data: A list of dictionaries containing market data with keys like 'price'.

    Returns:
    A string indicating the market trend ('bullish', 'bearish', or 'neutral').
    """
    if len(data) < 2:
        return 'neutral'

    price_changes = [item['price'] for item in data]
    if price_changes[-1] > price_changes[-2]:
        return 'bullish'
    elif price_changes[-1] < price_changes[-2]:
        return 'bearish'
    else:
        return 'neutral'