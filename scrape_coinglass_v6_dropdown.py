"""
🎯 SCRAPER COINGLASS V6 - CON SELECCIÓN CORRECTA DE MONEDA EN DROPDOWN
========================================================================

Este scraper:
1. Navega a CoinGlass
2. Hace clic en el dropdown de MONEDAS (cg-style-1gurlra)
3. Selecciona la moneda correcta (BTC, ETH, SOL)
4. Luego cambia a 5min
5. Extrae los datos
"""

import asyncio
import re
from playwright.async_api import async_playwright
from datetime import datetime


async def get_coinglass_exact(symbol: str = "BTC", interval: str = "5m") -> dict:
    """
    Extrae el ratio Long/Short de CoinGlass con selección correcta de moneda
    
    Args:
        symbol: Símbolo del activo (BTC, ETH, SOL, etc)
        interval: Temporalidad (siempre usa 5m)
        
    Returns:
        Dict con ratio y distribución
    """
    symbol = symbol.upper()
    print(f"🎯 [{datetime.now().strftime('%H:%M:%S')}] Scraping {symbol} (5min)...")
    print(f"   🌍 Environment: Headless Chromium with anti-detection")
    
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-gpu'
                ]
            )
            print(f"   ✅ Browser launched successfully")
        except Exception as e:
            print(f"   ❌ Failed to launch browser: {e}")
            return None
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Navegar a CoinGlass (puede ser cualquier moneda inicial)
            url = "https://www.coinglass.com/LongShortRatio"
            print(f"   📍 URL: {url}")
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                print(f"   ✅ Page loaded successfully")
            except Exception as nav_error:
                print(f"   ❌ Navigation failed: {nav_error}")
                await browser.close()
                return None
            
            await asyncio.sleep(1)
            
            # Cerrar popup de cookies
            try:
                for selector in ['button.fc-cta-consent', 'button:has-text("Consent")']:
                    btn = page.locator(selector).first
                    if await btn.count() > 0:
                        await btn.click(timeout=2000)
                        print(f"   ✅ Popup cerrado")
                        await asyncio.sleep(0.5)
                        break
            except:
                pass
            
            # Esperar overlay
            try:
                await page.wait_for_selector('div.fc-dialog-overlay', state='detached', timeout=3000)
            except:
                pass
            
            # 🔥 PASO CRÍTICO: SELECCIONAR LA MONEDA EN EL DROPDOWN
            print(f"   💰 Seleccionando moneda: {symbol}...")
            try:
                # Buscar TODOS los dropdowns con clase cg-style-1gurlra
                all_coin_dropdowns = await page.locator('div.cg-style-1gurlra').all()
                
                print(f"   📦 Encontrados {len(all_coin_dropdowns)} dropdowns cg-style-1gurlra")
                
                # Usar el ÚLTIMO dropdown (el de monedas)
                if all_coin_dropdowns:
                    coin_dropdown = all_coin_dropdowns[-1]
                    
                    # Ver qué moneda está seleccionada actualmente
                    current_coin_text = await coin_dropdown.text_content()
                    print(f"   🔍 Moneda actual en dropdown: '{current_coin_text.strip()}'")
                    
                    # Si no es la moneda que queremos, hacer clic y seleccionarla
                    if symbol not in current_coin_text.upper():
                        print(f"   🔄 Cambiando de {current_coin_text.strip()} a {symbol}...")
                        
                        # Hacer clic en el dropdown de monedas
                        await coin_dropdown.click()
                        await asyncio.sleep(1)
                        
                        # Buscar la opción con el símbolo correcto
                        # Intentar varios selectores posibles
                        option_found = False
                        for selector in [
                            f'li:has-text("{symbol}")',
                            f'[role="option"]:has-text("{symbol}")',
                            f'div:has-text("{symbol}")',
                        ]:
                            try:
                                option = page.locator(selector).first
                                if await option.count() > 0:
                                    await option.click(timeout=2000)
                                    print(f"   ✅ {symbol} seleccionado")
                                    option_found = True
                                    await asyncio.sleep(2)  # Esperar que cargue la nueva moneda
                                    break
                            except:
                                continue
                        
                        if not option_found:
                            print(f"   ⚠️ No se pudo hacer clic en {symbol}, intentando con teclado...")
                            # Fallback: usar teclado para buscar
                            await page.keyboard.type(symbol)
                            await asyncio.sleep(0.5)
                            await page.keyboard.press('Enter')
                            await asyncio.sleep(2)
                    else:
                        print(f"   ✅ Ya está en {symbol}")
                else:
                    print(f"   ⚠️ No se encontró dropdown de monedas")
            except Exception as e:
                print(f"   ⚠️ Error seleccionando moneda: {e}")
            
            # Ahora cambiar a 5 minutos
            print(f"   ⏱️  Configurando 5min...")
            try:
                all_dropdowns = await page.locator('button[role="combobox"].MuiSelect-button').all()
                
                time_dropdowns = []
                for dropdown in all_dropdowns:
                    text = await dropdown.text_content()
                    if any(word in text.lower() for word in ['hour', 'minute', 'min', 'day']):
                        time_dropdowns.append(dropdown)
                
                if time_dropdowns:
                    last_dropdown = time_dropdowns[-1]
                    current_interval = await last_dropdown.text_content()
                    print(f"   📊 Intervalo actual: '{current_interval.strip()}'")
                    
                    if "5 minute" not in current_interval and "5 min" not in current_interval:
                        print(f"   🔄 Cambiando a 5min...")
                        await last_dropdown.click(force=True)
                        await asyncio.sleep(1)
                        
                        for _ in range(4):
                            await page.keyboard.press('ArrowUp')
                            await asyncio.sleep(0.2)
                        
                        await page.keyboard.press('Enter')
                        await asyncio.sleep(3)
                        
                        new_interval = await last_dropdown.text_content()
                        print(f"   ✅ Nuevo intervalo: '{new_interval.strip()}'")
                    else:
                        print(f"   ✅ Ya está en 5min")
            except Exception as e:
                print(f"   ⚠️ Error cambiando intervalo: {e}")
            
            # Extraer datos
            print(f"   🔍 Buscando datos de Long/Short...")
            first_div = page.locator('div.cg-style-i4e4a6').first
            
            try:
                text = await first_div.text_content(timeout=5000)
                text = text.strip()
                print(f"   📝 Texto extraído: '{text}'")
                
                match = re.search(r'(\d+\.?\d*)\s*%', text)
                if match:
                    longs_pct = float(match.group(1))
                    shorts_pct = 100 - longs_pct
                    ratio = longs_pct / shorts_pct if shorts_pct > 0 else 1.0
                    
                    print(f"   ✅ {symbol}: LONG {longs_pct}% | SHORT {shorts_pct}%")
                    
                    await browser.close()
                    
                    return {
                        'longs_percent': round(longs_pct, 2),
                        'shorts_percent': round(shorts_pct, 2),
                        'ratio': round(ratio, 3),
                        'symbol': symbol,
                        'interval': '5m',
                        'source': 'coinglass_5min_dropdown',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    print(f"   ❌ No se encontró porcentaje en el texto")
            except Exception as e:
                print(f"   ❌ Error extrayendo datos: {e}")
            
            await browser.close()
            return None
            
        except Exception as e:
            print(f"   ❌ Error general: {e}")
            await browser.close()
            return None


async def test():
    """Probar cambio de símbolos con dropdown"""
    symbols = ['BTC', 'ETH', 'SOL']
    
    print("\n" + "="*60)
    print("🧪 PRUEBA DE CAMBIO DE SÍMBOLOS CON DROPDOWN")
    print("="*60 + "\n")
    
    for symbol in symbols:
        print(f"\n{'─'*60}")
        result = await get_coinglass_exact(symbol, "5m")
        
        if result:
            print(f"\n✅ RESULTADO PARA {symbol}:")
            print(f"   LONG:  {result['longs_percent']}%")
            print(f"   SHORT: {result['shorts_percent']}%")
            print(f"   RATIO: {result['ratio']}")
        else:
            print(f"\n❌ Error obteniendo datos de {symbol}")
        
        if symbol != symbols[-1]:
            print(f"\n⏳ Esperando 3 segundos antes del siguiente...")
            await asyncio.sleep(3)
    
    print(f"\n{'='*60}")
    print("✅ Prueba completada")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(test())
