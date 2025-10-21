"""
Data Adapter - Exchange Direct Integration + CoinGlass
Obtiene datos del exchange usando CCXT y complementa con CoinGlass

Datos calculados:
- Funding Rate (de exchange)
- Open Interest (de exchange) 
- Long/Short Ratio (desde CoinGlass API - DATOS REALES)
- Liquidation estimation (calculado desde OI y precio)
- Precio y volumen (directo)
- OHLCV histórico (directo)

¡NO REQUIERE API KEY para datos públicos!
"""

import asyncio
import ccxt.async_support as ccxt
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

# Importar CoinGlass adapter
try:
    from .coinglass_adapter import CoinGlassAdapter
    COINGLASS_AVAILABLE = True
except ImportError:
    COINGLASS_AVAILABLE = False
    print("⚠️ CoinGlass adapter no disponible, usando solo datos de exchange")


class ExchangeAdapter:
    """
    Adaptador que obtiene datos del exchange con CoinGlass para Long/Short ratio real
    """
    
    def __init__(self, exchange_name: str = 'binance', api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Inicializa el adaptador
        
        Args:
            exchange_name: Nombre del exchange (binance, bybit, okx, etc.)
            api_key: API key (OPCIONAL - solo para trading)
            api_secret: API secret (OPCIONAL - solo para trading)
        """
        self.exchange_name = exchange_name
        
        # Inicializar exchange con CCXT
        exchange_class = getattr(ccxt, exchange_name)
        
        config = {
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}  # Usar futuros por defecto
        }
        
        # API keys son opcionales - los datos públicos no los necesitan
        if api_key and api_secret:
            config['apiKey'] = api_key
            config['secret'] = api_secret
        
        self.exchange = exchange_class(config)
        
        # Inicializar CoinGlass adapter si está disponible
        self.coinglass = CoinGlassAdapter() if COINGLASS_AVAILABLE else None
        
        # Mapeo de símbolos
        self.symbol_map = {
            'BTC': 'BTC/USDT',
            'ETH': 'ETH/USDT',
            'SOL': 'SOL/USDT'
        }
    
    async def initialize(self):
        """Carga los mercados del exchange"""
        try:
            await self.exchange.load_markets()
            print(f"✅ Exchange {self.exchange_name} inicializado correctamente")
        except Exception as e:
            print(f"⚠️ Error inicializando exchange: {e}")
    
    async def close(self):
        """Cierra la conexión con el exchange"""
        await self.exchange.close()
    
    async def get_funding_rate(self, asset: str) -> Dict:
        """
        Obtiene Funding Rate DIRECTO del exchange
        
        Args:
            asset: Símbolo del activo (BTC, ETH, SOL)
            
        Returns:
            Dict con funding rate actual y predicho
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}/USDT")
            
            # Binance, Bybit, OKX proveen funding rate en sus APIs
            funding_data = await self.exchange.fetch_funding_rate(symbol)
            
            current_rate = funding_data.get('fundingRate', 0)
            next_rate = funding_data.get('nextFundingRate', current_rate)
            
            # Calcular promedio reciente
            funding_history = await self.exchange.fetch_funding_rate_history(
                symbol, 
                limit=24  # Últimas 24 horas
            )
            
            rates = [f['fundingRate'] for f in funding_history]
            avg_rate = np.mean(rates) if rates else current_rate
            
            return {
                'current': current_rate,
                'next': next_rate,
                'avg_24h': avg_rate,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo funding rate: {e}")
            # Retornar datos neutrales si falla
            return {
                'current': 0.0001,
                'next': 0.0001,
                'avg_24h': 0.0001,
                'symbol': symbol,
                'error': str(e)
            }
    
    async def get_open_interest(self, asset: str) -> Dict:
        """
        Obtiene Open Interest DIRECTO del exchange
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Dict con OI actual y cambio 24h
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}/USDT")
            
            # Obtener OI actual
            oi_data = await self.exchange.fetch_open_interest(symbol)
            current_oi = oi_data.get('openInterest', 0)
            
            # Obtener OI histórico para calcular cambio
            # Algunos exchanges tienen fetch_open_interest_history
            try:
                oi_history = await self.exchange.fetch_open_interest_history(
                    symbol,
                    timeframe='1h',
                    limit=24
                )
                
                if len(oi_history) >= 2:
                    oi_24h_ago = oi_history[0]['openInterest']
                    change_24h = current_oi - oi_24h_ago
                    change_24h_percent = (change_24h / oi_24h_ago * 100) if oi_24h_ago > 0 else 0
                else:
                    change_24h = 0
                    change_24h_percent = 0
                    
            except:
                # Si no hay histórico, asumir 0% de cambio
                change_24h = 0
                change_24h_percent = 0
            
            return {
                'current': current_oi,
                'change_24h': change_24h,
                'change_24h_percent': change_24h_percent,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo open interest: {e}")
            return {
                'current': 0,
                'change_24h': 0,
                'change_24h_percent': 0,
                'error': str(e)
            }
    
    async def get_long_short_ratio(self, asset: str) -> Dict:
        """
        Obtiene Long/Short Ratio REAL desde CoinGlass (web scraping + API)
        
        Fuentes (en orden de prioridad):
        1. CoinGlass web scraping - Datos REALES de posiciones abiertas
        2. CoinGlass API pública - Alternativa si scraping falla
        3. Binance Futures API - Fallback desde exchange
        4. Order book calculation - Última opción (aproximación)
        
        Args:
            asset: Símbolo del activo (BTC, ETH, SOL, etc.)
            
        Returns:
            Dict con ratio REAL y fuente de datos
        """
        
        # PRIORIDAD 1: CoinGlass (datos REALES)
        if self.coinglass:
            try:
                coinglass_data = await self.coinglass.get_long_short_ratio(asset)
                
                # Si CoinGlass devolvió datos válidos (no el fallback 50/50)
                if coinglass_data.get('source') != 'fallback':
                    print(f"✅ Long/Short ratio de {coinglass_data.get('source', 'coinglass')}: "
                          f"LONGS {coinglass_data['longs_percent']:.1f}% / "
                          f"SHORTS {coinglass_data['shorts_percent']:.1f}%")
                    return coinglass_data
                    
            except Exception as e:
                print(f"⚠️ CoinGlass no disponible: {e}")
        
        # FALLBACK: Calcular desde Order Book (APROXIMACIÓN)
        print(f"⚠️ Usando cálculo desde Order Book (aproximación)")
        try:
            symbol = self.symbol_map.get(asset, f"{asset}/USDT")
            
            # Obtener order book profundo
            orderbook = await self.exchange.fetch_order_book(symbol, limit=100)
            
            # Calcular volumen total en bids (compra) y asks (venta)
            bid_volume = sum([bid[1] for bid in orderbook['bids']])
            ask_volume = sum([ask[1] for ask in orderbook['asks']])
            
            # Ratio = bid_volume / ask_volume
            # > 1 = más compras (bullish)
            # < 1 = más ventas (bearish)
            ratio = bid_volume / ask_volume if ask_volume > 0 else 1.0
            
            longs_percent = (ratio / (ratio + 1)) * 100
            shorts_percent = (1 / (ratio + 1)) * 100
            
            return {
                'ratio': round(ratio, 3),
                'longs_percent': round(longs_percent, 2),
                'shorts_percent': round(shorts_percent, 2),
                'bid_volume': bid_volume,
                'ask_volume': ask_volume,
                'symbol': symbol,
                'source': 'orderbook_approximation',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Error calculando long/short ratio: {e}")
            return {
                'ratio': 1.0,
                'longs_percent': 50.0,
                'shorts_percent': 50.0,
                'source': 'error_fallback',
                'error': str(e)
            }
    
    async def get_liquidation_estimate(self, asset: str) -> Dict:
        """
        Estima zonas de liquidación probable
        
        Método: Basado en OI, leverage promedio y distribución de precio
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Dict con estimación de liquidaciones
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}/USDT")
            
            # Obtener precio actual
            ticker = await self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Obtener OI
            oi_data = await self.get_open_interest(asset)
            open_interest = oi_data['current']
            
            # Estimar leverage promedio (generalmente entre 2x y 10x)
            # En mercados volátiles, menor leverage; en estables, mayor
            volatility = await self._calculate_short_volatility(symbol)
            avg_leverage = 5.0 if volatility < 0.03 else 3.0
            
            # Calcular zonas de liquidación aproximadas
            # Longs se liquidan si el precio baja
            # Shorts se liquidan si el precio sube
            
            liquidation_margin = 1 / avg_leverage  # ej: 20% para 5x
            
            # Zona de liquidación de longs (abajo)
            long_liq_price = current_price * (1 - liquidation_margin)
            
            # Zona de liquidación de shorts (arriba)
            short_liq_price = current_price * (1 + liquidation_margin)
            
            # Estimar volumen que se liquidaría
            # Asumimos 50/50 long/short para simplicidad
            estimated_long_liq = open_interest * 0.5
            estimated_short_liq = open_interest * 0.5
            
            return {
                'current_price': current_price,
                'long_liquidation_price': round(long_liq_price, 2),
                'short_liquidation_price': round(short_liq_price, 2),
                'estimated_long_liquidations': estimated_long_liq,
                'estimated_short_liquidations': estimated_short_liq,
                'avg_leverage_estimate': avg_leverage,
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Error estimando liquidaciones: {e}")
            return {
                'error': str(e)
            }
    
    async def _calculate_short_volatility(self, symbol: str) -> float:
        """Calcula volatilidad reciente (últimas 24h)"""
        try:
            candles = await self.exchange.fetch_ohlcv(symbol, '1h', limit=24)
            closes = [c[4] for c in candles]
            returns = np.diff(closes) / closes[:-1]
            volatility = np.std(returns)
            return volatility
        except:
            return 0.02  # Default 2%
    
    async def get_current_price(self, asset: str) -> float:
        """
        Obtiene precio actual DIRECTO del exchange
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Precio actual
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}/USDT")
            ticker = await self.exchange.fetch_ticker(symbol)
            return ticker['last']
            
        except Exception as e:
            print(f"⚠️ Error obteniendo precio: {e}")
            return 0.0
    
    async def get_volume_24h(self, asset: str) -> float:
        """
        Obtiene volumen 24h DIRECTO del exchange
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Volumen en USD
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}/USDT")
            ticker = await self.exchange.fetch_ticker(symbol)
            
            # Volumen en quote currency (USDT)
            volume_24h = ticker.get('quoteVolume', 0)
            
            return volume_24h
            
        except Exception as e:
            print(f"⚠️ Error obteniendo volumen: {e}")
            return 0.0
    
    async def get_ohlcv(self, asset: str, timeframe: str = '4h', limit: int = 100) -> List[Dict]:
        """
        Obtiene velas OHLCV DIRECTAS del exchange
        
        Args:
            asset: Símbolo del activo
            timeframe: Temporalidad (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Número de velas
            
        Returns:
            Lista de velas con open, high, low, close, volume
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}/USDT")
            
            # Fetch OHLCV desde exchange
            ohlcv = await self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Convertir a formato dict
            candles = []
            for candle in ohlcv:
                candles.append({
                    'timestamp': datetime.fromtimestamp(candle[0] / 1000).isoformat(),
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            
            return candles
            
        except Exception as e:
            print(f"⚠️ Error obteniendo OHLCV: {e}")
            return []
    
    async def fetch_all_data(self, asset: str) -> Dict:
        """
        Obtiene TODOS los datos necesarios en paralelo
        DIRECTAMENTE del exchange, sin servicios externos
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Dict con todos los datos
        """
        try:
            # Ejecutar todas las llamadas en paralelo
            results = await asyncio.gather(
                self.get_funding_rate(asset),
                self.get_open_interest(asset),
                self.get_long_short_ratio(asset),
                self.get_liquidation_estimate(asset),
                self.get_current_price(asset),
                self.get_volume_24h(asset),
                return_exceptions=True
            )
            
            return {
                'funding_rate': results[0] if not isinstance(results[0], Exception) else {},
                'open_interest': results[1] if not isinstance(results[1], Exception) else {},
                'long_short_ratio': results[2] if not isinstance(results[2], Exception) else {},
                'liquidations': results[3] if not isinstance(results[3], Exception) else {},
                'current_price': results[4] if not isinstance(results[4], Exception) else 0,
                'volume_24h': results[5] if not isinstance(results[5], Exception) else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"⚠️ Error obteniendo datos completos: {e}")
            return {}


# Función auxiliar para testing
async def test_adapter():
    """Función de prueba del adaptador"""
    print("🧪 Testing Exchange Adapter (SIN CoinGlass)...")
    
    adapter = ExchangeAdapter('binance')
    await adapter.initialize()
    
    assets = ['BTC', 'ETH', 'SOL']
    
    for asset in assets:
        print(f"\n📊 Testing {asset}...")
        
        # Test individual
        print(f"\n  1. Funding Rate...")
        funding = await adapter.get_funding_rate(asset)
        print(f"     Current: {funding.get('current', 0):.4%}")
        
        print(f"\n  2. Open Interest...")
        oi = await adapter.get_open_interest(asset)
        print(f"     Current: ${oi.get('current', 0):,.0f}")
        
        print(f"\n  3. Long/Short Ratio...")
        ls = await adapter.get_long_short_ratio(asset)
        print(f"     Ratio: {ls.get('ratio', 0):.2f}")
        
        print(f"\n  4. Price...")
        price = await adapter.get_current_price(asset)
        print(f"     Price: ${price:,.2f}")
        
        # Test completo
        print(f"\n  5. Fetch All Data...")
        all_data = await adapter.fetch_all_data(asset)
        print(f"     ✅ Todos los datos obtenidos")
    
    await adapter.close()
    print("\n✅ Test completed!")


if __name__ == "__main__":
    # Ejecutar test
    asyncio.run(test_adapter())
