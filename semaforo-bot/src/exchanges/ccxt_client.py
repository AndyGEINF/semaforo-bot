class CCXTClient:
    def __init__(self, exchange_name, api_key=None, secret=None, password=None):
        import ccxt
        
        self.exchange = getattr(ccxt, exchange_name)({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
        })

    def fetch_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)

    def fetch_ohlcv(self, symbol, timeframe='1m', limit=100):
        return self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    def fetch_balance(self):
        return self.exchange.fetch_balance()

    def create_order(self, symbol, order_type, side, amount, price=None, params={}):
        return self.exchange.create_order(symbol, order_type, side, amount, price, params)

    def fetch_markets(self):
        return self.exchange.fetch_markets()