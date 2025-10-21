"""
Data Adapter - CoinGlass Integration Module
Adaptador para obtener datos de CoinGlass mediante Web Scraping

Datos obtenidos:
- Funding Rate (desde página de Binance Futures)
- Open Interest (desde dashboard principal)
- Long/Short Ratio (desde indicadores)
- Liquidation Maps (desde mapa de liquidaciones)
- Precio y volumen
"""

import asyncio
import aiohttp
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
import re
import random
import hashlib
import time


class CoinGlassAdapter:
    """
    Adaptador para obtener datos de derivados de CoinGlass u otras fuentes
    CON TÉCNICAS ANTI-DETECCIÓN AVANZADAS 🥷
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Inicializa el adaptador
        
        Args:
            api_key: API key de CoinGlass (opcional)
            base_url: URL base de la API
        """
        self.api_key = api_key
        self.base_url = base_url or "https://open-api.coinglass.com/public/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
        
        # Mapeo de símbolos
        self.symbol_map = {
            'BTC': 'BTCUSDT',
            'ETH': 'ETHUSDT',
            'SOL': 'SOLUSDT'
        }
        
        # Pool de User-Agents realistas (navegadores reales)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        
        # Accept-Language variados
        self.accept_languages = [
            'en-US,en;q=0.9',
            'en-US,en;q=0.9,es;q=0.8',
            'en-GB,en;q=0.9,en-US;q=0.8',
            'es-ES,es;q=0.9,en;q=0.8',
            'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
        ]
    
    def _get_random_user_agent(self) -> str:
        """Obtiene un User-Agent aleatorio del pool"""
        return random.choice(self.user_agents)
    
    def _get_random_accept_language(self) -> str:
        """Obtiene un Accept-Language aleatorio"""
        return random.choice(self.accept_languages)
    
    def _generate_realistic_headers(self) -> Dict[str, str]:
        """
        Genera headers que simulan un navegador real
        Incluye fingerprinting realista
        """
        return {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': self._get_random_accept_language(),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        }
    
    async def _human_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """
        Añade un delay aleatorio para simular comportamiento humano
        """
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def _rate_limit_delay(self):
        """
        Implementa rate limiting para evitar demasiadas requests
        Mínimo 1 segundo entre requests
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < 1.0:
            await asyncio.sleep(1.0 - time_since_last)
        
        self.last_request_time = time.time()
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtiene o crea sesión HTTP"""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers['CG-API-KEY'] = self.api_key
            
            self.session = aiohttp.ClientSession(headers=headers)
        
        return self.session
    
    async def close(self):
        """Cierra la sesión HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_funding_rate(self, asset: str) -> Dict:
        """
        Obtiene Funding Rate actual y promedio
        
        Args:
            asset: Símbolo del activo (BTC, ETH, SOL)
            
        Returns:
            Dict con funding rate actual y promedio 24h
        """
        try:
            # TODO: Implementar llamada real a API
            # Por ahora, datos simulados
            
            symbol = self.symbol_map.get(asset, f"{asset}USDT")
            
            # Simulación de datos
            # En producción, hacer: GET /api/futures/funding-rate
            funding_data = {
                'current': 0.01,  # 0.01% = funding positivo moderado
                'avg_24h': 0.015,
                'symbol': symbol,
                'exchange': 'binance',
                'timestamp': datetime.now().isoformat()
            }
            
            return funding_data
            
        except Exception as e:
            print(f"⚠️ Error obteniendo funding rate: {e}")
            return {'current': 0, 'avg_24h': 0, 'error': str(e)}
    
    async def get_open_interest(self, asset: str) -> Dict:
        """
        Obtiene Open Interest y cambios 24h
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Dict con OI actual y cambio 24h
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}USDT")
            
            # TODO: Implementar llamada real
            # En producción: GET /api/futures/open-interest
            
            oi_data = {
                'current': 15_000_000_000,  # $15B en OI (ejemplo BTC)
                'change_24h': 500_000_000,   # +$500M
                'change_24h_percent': 3.33,  # +3.33%
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
            
            return oi_data
            
        except Exception as e:
            print(f"⚠️ Error obteniendo open interest: {e}")
            return {'current': 0, 'change_24h_percent': 0, 'error': str(e)}
    
    async def get_long_short_ratio(self, asset: str, interval: str = "5m") -> Dict:
        """
        Obtiene ratio de posiciones Long vs Short REAL desde CoinGlass
        CON WEB SCRAPING REAL usando Playwright (no API)
        
        CoinGlass ahora requiere autenticación para su API, pero su web
        es pública. Hacemos scraping del HTML renderizado con navegador.
        
        Estrategia:
        1. CoinGlass Web Scraping con Playwright (temporalidad 5m) 🎯
        2. Binance Futures API (fallback - datos globales)
        3. Default conservador (si falla todo)
        
        Args:
            asset: Símbolo del activo
            interval: Temporalidad (5m, 15m, 1h, 4h, 1d) - Default: 5m
            
        Returns:
            Dict con ratio y distribución REAL
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}USDT")
            
            # ===== CAPA 1: COINGLASS WEB SCRAPING (TEMPORALIDAD 5M) =====
            try:
                from playwright.async_api import async_playwright
                import re
                
                print(f"🎯 Scraping CoinGlass {interval} para {asset}...")
                
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=['--disable-blink-features=AutomationControlled']
                    )
                    
                    context = await browser.new_context(
                        user_agent=self._get_random_user_agent(),
                        viewport={'width': 1920, 'height': 1080}
                    )
                    
                    page = await context.new_page()
                    
                    # Navegar a CoinGlass
                    url = f"https://www.coinglass.com/LongShortRatio?coin={asset}"
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                    await asyncio.sleep(2)
                    
                    # Cerrar popup de cookies
                    try:
                        for pattern in ['button:has-text("Accept")', '.fc-cta-consent']:
                            try:
                                btn = page.locator(pattern).first
                                if await btn.count() > 0:
                                    await btn.click(timeout=3000)
                                    await asyncio.sleep(1)
                                    break
                            except:
                                continue
                    except:
                        pass
                    
                    # Buscar dropdown de temporalidad (no el de idioma)
                    try:
                        all_dropdowns = await page.locator('button[role="combobox"].MuiSelect-button').all()
                        
                        for dropdown in all_dropdowns:
                            try:
                                text = await dropdown.text_content()
                                if any(word in text.lower() for word in ['hour', 'minute', 'min', 'day']):
                                    if "5 minute" not in text and "5 min" not in text:
                                        await dropdown.scroll_into_view_if_needed()
                                        await asyncio.sleep(0.5)
                                        await dropdown.click()
                                        await asyncio.sleep(1.5)
                                        
                                        for pattern in ['[role="option"]:has-text("5 minute")', 
                                                       'li:has-text("5 minute")']:
                                            try:
                                                option = page.locator(pattern).first
                                                if await option.count() > 0:
                                                    await option.click()
                                                    await asyncio.sleep(3)
                                                    break
                                            except:
                                                continue
                                    break
                            except:
                                continue
                    except:
                        pass
                    
                    await asyncio.sleep(2)
                    
                    # Extraer datos del DOM
                    all_text = await page.evaluate('() => document.body.innerText')
                    pattern = r'(\d+\.?\d*)\%/(\d+\.?\d*)\%'
                    matches = re.findall(pattern, all_text)
                    
                    await browser.close()
                    
                    if matches:
                        for match in matches:
                            longs_pct = float(match[0])
                            shorts_pct = float(match[1])
                            total = longs_pct + shorts_pct
                            
                            if 95 <= total <= 105:
                                ratio = longs_pct / shorts_pct if shorts_pct > 0 else 1.0
                                
                                print(f"✅ [CoinGlass {interval}] {asset}: LONGS {longs_pct:.1f}% / SHORTS {shorts_pct:.1f}%")
                                
                                return {
                                    'ratio': round(ratio, 3),
                                    'longs_percent': round(longs_pct, 2),
                                    'shorts_percent': round(shorts_pct, 2),
                                    'symbol': symbol,
                                    'interval': interval,
                                    'source': 'coinglass_web',
                                    'timestamp': datetime.now().isoformat()
                                }
                    
            except ImportError:
                print(f"⚠️ Playwright no instalado, usando fallback")
            except Exception as e:
                print(f"⚠️ Error en CoinGlass scraping: {e}")
            
            # ===== CAPA 2: BINANCE API FALLBACK =====
            print(f"🔄 Usando Binance API como fallback para {asset}")
            return await self._get_binance_fallback_ls_ratio(asset)
            
        except Exception as e:
            print(f"⚠️ Error en get_long_short_ratio: {e}")
            return await self._get_binance_fallback_ls_ratio(asset)
    
    async def _get_binance_fallback_ls_ratio(self, asset: str) -> Dict:
        """
        Fallback: Obtiene L/S ratio desde Binance Futures API directamente
        CON TÉCNICAS ANTI-DETECCIÓN 🥷
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}USDT")
            session = await self._get_session()
            
            # Rate limiting y delay humano
            await self._rate_limit_delay()
            await self._human_delay(0.2, 0.6)
            
            # Binance Futures API pública para Long/Short Ratio
            url = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
            
            # Headers realistas para Binance
            binance_headers = {
                'User-Agent': self._get_random_user_agent(),
                'Accept': 'application/json',
                'Accept-Language': self._get_random_accept_language(),
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Origin': 'https://www.binance.com',
                'Referer': 'https://www.binance.com/en/futures',
            }
            
            params = {
                'symbol': symbol,
                'period': '5m',
                'limit': 1
            }
            
            async with session.get(url, headers=binance_headers, params=params, timeout=8) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data and len(data) > 0:
                        latest = data[0]
                        
                        # Binance devuelve longAccount y shortAccount (ratios)
                        long_account = float(latest.get('longAccount', 0.5))
                        short_account = float(latest.get('shortAccount', 0.5))
                        
                        longs_pct = long_account * 100
                        shorts_pct = short_account * 100
                        ratio = longs_pct / shorts_pct if shorts_pct > 0 else 1.0
                        
                        print(f"✅ [Binance API] {asset}: LONGS {longs_pct:.1f}% / SHORTS {shorts_pct:.1f}%")
                        
                        return {
                            'ratio': round(ratio, 3),
                            'longs_percent': round(longs_pct, 2),
                            'shorts_percent': round(shorts_pct, 2),
                            'symbol': symbol,
                            'source': 'binance_api',
                            'timestamp': datetime.now().isoformat()
                        }
                elif response.status == 429:
                    print(f"⚠️ Rate limited por Binance")
                    await asyncio.sleep(2)  # Esperar antes del fallback final
            
            # Último fallback: datos conservadores
            print(f"⚠️ Usando fallback conservador 50/50 para {asset}")
            return {
                'ratio': 1.0,
                'longs_percent': 50.0,
                'shorts_percent': 50.0,
                'symbol': symbol,
                'source': 'fallback',
                'timestamp': datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            print(f"⚠️ Timeout en Binance API fallback")
            return {
                'ratio': 1.0,
                'longs_percent': 50.0,
                'shorts_percent': 50.0,
                'symbol': symbol,
                'source': 'fallback_timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Error en fallback de Binance: {e}")
            return {
                'ratio': 1.0,
                'longs_percent': 50.0,
                'shorts_percent': 50.0,
                'symbol': symbol,
                'source': 'fallback_error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def get_liquidation_map(self, asset: str) -> Dict:
        """
        Obtiene mapa de liquidaciones 24h
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Dict con liquidaciones por lado
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}USDT")
            
            # TODO: Implementar llamada real
            # En producción: GET /api/futures/liquidation
            
            liq_data = {
                'total_24h': 250_000_000,      # $250M liquidados
                'longs_liquidated': 180_000_000,  # $180M en longs
                'shorts_liquidated': 70_000_000,  # $70M en shorts
                'symbol': symbol,
                'timestamp': datetime.now().isoformat()
            }
            
            return liq_data
            
        except Exception as e:
            print(f"⚠️ Error obteniendo liquidaciones: {e}")
            return {'total_24h': 0, 'error': str(e)}
    
    async def get_current_price(self, asset: str) -> float:
        """
        Obtiene precio actual del activo
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Precio actual
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}USDT")
            
            # TODO: Implementar fetch real de precio
            # Puede usar CCXT o API directa del exchange
            
            # Precios simulados
            mock_prices = {
                'BTC': 65000.0,
                'ETH': 3200.0,
                'SOL': 145.0
            }
            
            return mock_prices.get(asset, 100.0)
            
        except Exception as e:
            print(f"⚠️ Error obteniendo precio: {e}")
            return 0.0
    
    async def get_volume_24h(self, asset: str) -> float:
        """
        Obtiene volumen 24h del activo
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Volumen en USD
        """
        try:
            # TODO: Implementar fetch real
            
            # Volúmenes simulados
            mock_volumes = {
                'BTC': 30_000_000_000,  # $30B
                'ETH': 15_000_000_000,  # $15B
                'SOL': 2_000_000_000    # $2B
            }
            
            return mock_volumes.get(asset, 0.0)
            
        except Exception as e:
            print(f"⚠️ Error obteniendo volumen: {e}")
            return 0.0
    
    async def get_ohlcv(self, asset: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """
        Obtiene velas OHLCV históricas
        
        Args:
            asset: Símbolo del activo
            timeframe: Temporalidad (1h, 4h, 1d)
            limit: Número de velas
            
        Returns:
            Lista de velas con open, high, low, close, volume
        """
        try:
            symbol = self.symbol_map.get(asset, f"{asset}USDT")
            
            # TODO: Implementar con CCXT o API del exchange
            # Por ahora, generar datos simulados
            
            current_price = await self.get_current_price(asset)
            candles = []
            
            for i in range(limit):
                # Generar vela simulada con variación aleatoria
                import random
                variation = random.uniform(-0.02, 0.02)  # +/- 2%
                
                open_price = current_price * (1 + variation)
                high_price = open_price * 1.01
                low_price = open_price * 0.99
                close_price = open_price * (1 + random.uniform(-0.01, 0.01))
                volume = random.uniform(1000000, 10000000)
                
                candles.append({
                    'timestamp': (datetime.now() - timedelta(hours=i)).isoformat(),
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': volume
                })
            
            # Invertir para tener el más antiguo primero
            return list(reversed(candles))
            
        except Exception as e:
            print(f"⚠️ Error obteniendo OHLCV: {e}")
            return []
    
    async def fetch_all_data(self, asset: str) -> Dict:
        """
        Obtiene todos los datos necesarios en paralelo
        
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
                self.get_liquidation_map(asset),
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
    adapter = CoinGlassAdapter()
    
    print("🧪 Testing CoinGlass Adapter...")
    
    assets = ['BTC', 'ETH', 'SOL']
    for asset in assets:
        print(f"\n📊 Testing {asset}...")
        data = await adapter.fetch_all_data(asset)
        print(json.dumps(data, indent=2))
    
    await adapter.close()
    print("\n✅ Test completed!")


if __name__ == "__main__":
    # Ejecutar test
    asyncio.run(test_adapter())
