# 🎯 INSTRUCCIONES COMPLETAS: Scraping CoinGlass Long/Short Ratio

## 📋 CONTEXTO Y OBJETIVO

**Objetivo**: Extraer datos de Long/Short Ratio de CoinGlass para diferentes criptomonedas (BTC, ETH, SOL) con intervalo de 5 minutos.

**URL Base**: `https://www.coinglass.com/LongShortRatio`

**Problema Crítico Identificado**: 
- ❌ Cambiar solo el parámetro URL `?coin=ETH` NO es suficiente
- ✅ Es OBLIGATORIO hacer clic en el dropdown de selección de moneda
- ✅ El dropdown tiene la clase CSS `cg-style-1gurlra`

---

## 🔧 TECNOLOGÍA REQUERIDA

```python
# Dependencias necesarias
from playwright.async_api import async_playwright
import asyncio
import re
from datetime import datetime
```

**Motor**: Playwright (navegador headless Chromium)

**Configuración del navegador**:
```python
browser = await p.chromium.launch(
    headless=True,
    args=[
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--disable-setuid-sandbox',
        '--no-sandbox'
    ]
)

context = await browser.new_context(
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    viewport={'width': 1920, 'height': 1080},
    locale='en-US'
)
```

---

## 🎯 PROCESO DE SCRAPING (PASO A PASO)

### **PASO 1: Navegación Inicial**

```python
# Navegar a la página principal (SIN parámetro coin en la URL)
await page.goto('https://www.coinglass.com/LongShortRatio', 
                wait_until='domcontentloaded',
                timeout=60000)

# Esperar a que la página cargue
await page.wait_for_timeout(3000)
```

**⚠️ IMPORTANTE**: No incluir `?coin=SYMBOL` en la URL inicial, el símbolo se selecciona desde el dropdown.

---

### **PASO 2: Cerrar Popup de Cookies (si aparece)**

```python
try:
    # Buscar y cerrar el popup de cookies
    close_button = await page.query_selector('button:has-text("Close")')
    if close_button:
        await close_button.click()
        await page.wait_for_timeout(500)
        print("   ✅ Popup cerrado")
except:
    pass  # No hay popup, continuar
```

---

### **PASO 3: SELECCIÓN DE MONEDA (CRÍTICO) 🔴**

Este es el paso MÁS IMPORTANTE. El dropdown tiene clase `cg-style-1gurlra` y hay MÚLTIPLES dropdowns en la página:

```python
# 1. Encontrar TODOS los dropdowns con esa clase
all_dropdowns = await page.query_selector_all('button.cg-style-1gurlra')
print(f"   📦 Encontrados {len(all_dropdowns)} dropdowns cg-style-1gurlra")

# 2. Identificar el dropdown de MONEDA (no el de tiempo)
coin_dropdown = None
for dropdown in all_dropdowns:
    text = await dropdown.text_content()
    # El dropdown de moneda contiene símbolos como BTC, ETH, SOL
    # El dropdown de tiempo contiene "5 minute", "4 hour", etc.
    if text and not any(time_word in text.lower() for time_word in ['minute', 'hour', 'day']):
        coin_dropdown = dropdown
        print(f"   🔍 Moneda actual en dropdown: '{text}'")
        break

if not coin_dropdown:
    raise Exception("❌ No se encontró el dropdown de moneda")

# 3. Hacer clic en el dropdown para abrirlo
print(f"   🔄 Cambiando de {await coin_dropdown.text_content()} a {symbol}...")
await coin_dropdown.click()
await page.wait_for_timeout(1000)

# 4. Buscar la opción de la moneda deseada en el menú
coin_option = None
options = await page.query_selector_all('[role="menuitem"], [role="option"]')

for option in options:
    option_text = await option.text_content()
    if option_text and symbol.upper() in option_text.upper():
        coin_option = option
        break

if not coin_option:
    raise Exception(f"❌ No se encontró la opción {symbol} en el menú")

# 5. Hacer clic en la opción de la moneda
await coin_option.click()
await page.wait_for_timeout(2000)

# 6. VERIFICAR que se seleccionó correctamente
selected_text = await coin_dropdown.text_content()
print(f"   ✅ Coin dropdown ahora muestra: '{selected_text}'")

if symbol.upper() not in selected_text.upper():
    raise Exception(f"❌ Error: se esperaba {symbol} pero el dropdown muestra '{selected_text}'")
```

**🔴 REGLAS CRÍTICAS**:
1. Hay MÚLTIPLES dropdowns `cg-style-1gurlra` en la página
2. Debes identificar cuál es el de MONEDA (no el de tiempo)
3. El de moneda NO contiene palabras como "minute", "hour", "day"
4. SIEMPRE verificar que la selección fue exitosa leyendo el texto del dropdown después

---

### **PASO 4: Cambiar Intervalo a 5 Minutos**

```python
# 1. Encontrar el dropdown de TIEMPO (el que sí contiene "minute", "hour")
time_dropdown = None
all_dropdowns = await page.query_selector_all('button.cg-style-1gurlra')

for dropdown in all_dropdowns:
    text = await dropdown.text_content()
    if text and any(time_word in text.lower() for time_word in ['minute', 'hour', 'day']):
        time_dropdown = dropdown
        print(f"   📊 Intervalo actual: '{text}'")
        break

if not time_dropdown:
    raise Exception("❌ No se encontró el dropdown de intervalo")

# 2. Si no está en 5min, cambiarlo
current_interval = await time_dropdown.text_content()
if '5 minute' not in current_interval.lower():
    print(f"   🔄 Cambiando a 5min...")
    await time_dropdown.click()
    await page.wait_for_timeout(1000)
    
    # Buscar la opción "5 minute"
    options = await page.query_selector_all('[role="menuitem"], [role="option"]')
    for option in options:
        option_text = await option.text_content()
        if option_text and '5 minute' in option_text.lower():
            await option.click()
            await page.wait_for_timeout(2000)
            break
    
    # Verificar cambio
    new_interval = await time_dropdown.text_content()
    print(f"   ✅ Nuevo intervalo: '{new_interval}'")
```

---

### **PASO 5: Esperar Carga de Datos**

```python
# Esperar a que los datos se actualicen después de cambiar moneda e intervalo
await page.wait_for_timeout(3000)

# Esperar a que aparezcan los elementos con los porcentajes
await page.wait_for_selector('text=/[0-9]+\.[0-9]+%/', timeout=30000)
```

---

### **PASO 6: Extracción de Datos Long/Short**

```python
print(f"   🔍 Buscando datos de Long/Short...")

# Buscar TODOS los elementos que contengan porcentajes
percentage_elements = await page.query_selector_all('text=/[0-9]+\.[0-9]+%/')

if not percentage_elements or len(percentage_elements) < 2:
    raise Exception(f"❌ No se encontraron suficientes porcentajes (encontrados: {len(percentage_elements)})")

# Los primeros dos porcentajes visibles son LONG y SHORT
long_element = percentage_elements[0]
short_element = percentage_elements[1]

# Extraer texto
long_text = await long_element.text_content()
short_text = await short_element.text_content()

print(f"   📝 Texto extraído: '{long_text}' y '{short_text}'")

# Parsear porcentajes con regex
long_match = re.search(r'([0-9]+\.?[0-9]*)', long_text)
short_match = re.search(r'([0-9]+\.?[0-9]*)', short_text)

if not long_match or not short_match:
    raise Exception("❌ No se pudieron parsear los porcentajes")

long_pct = float(long_match.group(1))
short_pct = float(short_match.group(1))

# Validar que sumen aproximadamente 100%
total = long_pct + short_pct
if not (99 <= total <= 101):
    raise Exception(f"❌ Porcentajes inválidos: {long_pct}% + {short_pct}% = {total}%")

print(f"   ✅ {symbol}: LONG {long_pct}% | SHORT {short_pct}%")

return {
    'symbol': symbol,
    'long_percent': long_pct,
    'short_percent': short_pct,
    'ratio': round(long_pct / short_pct, 3) if short_pct > 0 else 0,
    'interval': '5m',
    'timestamp': datetime.now().isoformat(),
    'source': 'coinglass'
}
```

---

## 🎯 ESTRUCTURA DE DATOS DE SALIDA

```python
{
    "symbol": "ETH",           # Símbolo de la criptomoneda
    "long_percent": 66.51,     # Porcentaje de posiciones Long
    "short_percent": 33.49,    # Porcentaje de posiciones Short
    "ratio": 1.986,            # Ratio Long/Short
    "interval": "5m",          # Intervalo de tiempo
    "timestamp": "2025-10-19T18:41:21",  # Timestamp ISO
    "source": "coinglass"      # Fuente de los datos
}
```

---

## ⚠️ ERRORES COMUNES Y SOLUCIONES

### **Error 1: Datos de la moneda incorrecta**
❌ **Problema**: Cambiar URL pero no hacer clic en dropdown
✅ **Solución**: SIEMPRE hacer clic en el dropdown `cg-style-1gurlra` para seleccionar moneda

### **Error 2: Timeout esperando selectores**
❌ **Problema**: Selectores específicos que cambian
✅ **Solución**: Usar selectores de texto con regex `text=/[0-9]+\.[0-9]+%/`

### **Error 3: Click en dropdown equivocado**
❌ **Problema**: Hacer clic en dropdown de tiempo en lugar de moneda
✅ **Solución**: Filtrar dropdowns verificando que NO contengan "minute", "hour", "day"

### **Error 4: Popup de cookies bloquea interacción**
❌ **Problema**: No cerrar el popup de cookies
✅ **Solución**: Siempre intentar cerrar `button:has-text("Close")` al inicio

### **Error 5: Porcentajes no suman 100%**
❌ **Problema**: Extraer porcentajes de diferentes secciones
✅ **Solución**: Tomar los primeros DOS elementos encontrados con regex de porcentaje

---

## 🔄 MANEJO DE MÚLTIPLES SÍMBOLOS

Para cambiar entre símbolos (BTC → ETH → SOL):

```python
async def scrape_multiple_symbols():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(...)
        page = await context.new_page()
        
        # Navegar UNA VEZ
        await page.goto('https://www.coinglass.com/LongShortRatio')
        await page.wait_for_timeout(3000)
        
        # Cerrar popup UNA VEZ
        try:
            close_btn = await page.query_selector('button:has-text("Close")')
            if close_btn:
                await close_btn.click()
        except:
            pass
        
        results = {}
        
        # Iterar símbolos
        for symbol in ['BTC', 'ETH', 'SOL']:
            # Seleccionar moneda desde dropdown
            await select_coin_from_dropdown(page, symbol)
            
            # Asegurar intervalo 5min
            await set_interval_5min(page)
            
            # Extraer datos
            data = await extract_longshort_data(page, symbol)
            results[symbol] = data
            
            # Esperar antes del siguiente
            await page.wait_for_timeout(2000)
        
        await browser.close()
        return results
```

**⚠️ NO cerrar y reabrir el navegador entre símbolos** - es más eficiente reutilizar la misma página.

---

## 📊 VALIDACIONES IMPORTANTES

```python
# 1. Verificar que el dropdown cambió
selected_text = await coin_dropdown.text_content()
assert symbol.upper() in selected_text.upper(), f"Dropdown no cambió a {symbol}"

# 2. Verificar que hay suficientes porcentajes
assert len(percentage_elements) >= 2, "Faltan porcentajes en la página"

# 3. Verificar que suman ~100%
total = long_pct + short_pct
assert 99 <= total <= 101, f"Porcentajes inválidos: {total}%"

# 4. Verificar que son números válidos
assert 0 <= long_pct <= 100, f"Long % fuera de rango: {long_pct}"
assert 0 <= short_pct <= 100, f"Short % fuera de rango: {short_pct}"
```

---

## 🚀 CÓDIGO COMPLETO DE REFERENCIA

Archivo de referencia exitoso: **`scrape_coinglass_v6_dropdown.py`**

Puntos clave del código:
- Líneas 60-105: Lógica de selección de moneda desde dropdown
- Líneas 107-145: Cambio de intervalo a 5min
- Líneas 147-185: Extracción y validación de datos Long/Short

---

## 📝 NOTAS FINALES

1. **Tiempo de espera**: Usar `await page.wait_for_timeout()` entre acciones (1000-3000ms)
2. **User Agent**: Simular navegador real para evitar detección
3. **Headless**: Puede ejecutarse sin interfaz gráfica
4. **Robustez**: Siempre verificar que los selectores existen antes de interactuar
5. **Logging**: Imprimir cada paso para debugging (emoji + descripción)

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Instalar Playwright: `pip install playwright && playwright install chromium`
- [ ] Configurar navegador con User-Agent y viewport
- [ ] Navegar a URL base (sin parámetros)
- [ ] Cerrar popup de cookies
- [ ] **CRÍTICO**: Identificar dropdown de MONEDA (clase `cg-style-1gurlra`, sin palabras de tiempo)
- [ ] Hacer clic en dropdown de moneda
- [ ] Buscar y hacer clic en opción de moneda deseada
- [ ] Verificar que dropdown muestra la moneda correcta
- [ ] Cambiar intervalo a "5 minute"
- [ ] Esperar carga de datos (3 segundos)
- [ ] Extraer primeros dos porcentajes visibles
- [ ] Validar que suman ~100%
- [ ] Retornar datos en formato estructurado

---

## 🎯 RESULTADO ESPERADO

Al ejecutar el scraper para BTC, ETH y SOL, deberías obtener **DATOS DIFERENTES**:

```
✅ BTC: LONG 53.07% | SHORT 46.93% | RATIO 1.131
✅ ETH: LONG 66.51% | SHORT 33.49% | RATIO 1.986
✅ SOL: LONG 38.72% | SHORT 61.28% | RATIO 0.632
```

Si todos los símbolos muestran los mismos porcentajes, significa que **NO se está haciendo clic en el dropdown** correctamente.

---

**Fecha de creación**: 2025-10-19  
**Versión del scraper**: v6 (dropdown)  
**Estado**: ✅ Probado y funcionando correctamente
