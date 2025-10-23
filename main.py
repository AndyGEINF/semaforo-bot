"""
SemáforoBot - Main Entry Point
Bot de trading modular con análisis de riesgo y memoria persistente

Comandos disponibles:
- semaforo: Análisis de riesgo completo
- operar [ASSET] [TIMEFRAME] [DURATION]: Calcula entrada óptima
- confirmar trade: Ejecuta el trade pendiente
- configurar stoploss [%] tp [%]: Ajusta parámetros de riesgo
"""

import os
import json
import asyncio
from typing import Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uvicorn

# Importar módulos internos
from strategy.risk_analyzer import RiskAnalyzer
from strategy.entry_optimizer import EntryOptimizer
from strategy.memory_manager import MemoryManager
from data_adapter.exchange_adapter import ExchangeAdapter  # ← Cambiado de CoinGlass
from redis_store import RedisStore

# Cargar variables de entorno
load_dotenv()

# Cargar configuración
with open('config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

# Inicializar FastAPI
app = FastAPI(
    title="SemáforoBot API",
    description="Bot de trading con análisis de riesgo automatizado",
    version=CONFIG['version']
)

# Configurar CORS para permitir acceso desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar directorio estático
app.mount("/static", StaticFiles(directory="static"), name="static")

# Estado global del bot
class BotState:
    """Gestión del estado global del bot"""
    def __init__(self):
        self.redis_store: Optional[RedisStore] = None
        self.risk_analyzer: Optional[RiskAnalyzer] = None
        self.entry_optimizer: Optional[EntryOptimizer] = None
        self.memory_manager: Optional[MemoryManager] = None
        self.data_adapter: Optional[ExchangeAdapter] = None  # ← Cambiado tipo
        self.pending_trade: Optional[Dict] = None
        self.active_trades: Dict[str, Dict] = {}

bot_state = BotState()


# Modelos de datos para API
class AnalyzeRequest(BaseModel):
    """Modelo para solicitud de análisis de semáforo"""
    assets: Optional[list[str]] = Field(default=None, description="Lista de activos a analizar")
    force_refresh: bool = Field(default=False, description="Forzar actualización de datos")

class TradeRequest(BaseModel):
    """Modelo para solicitud de operación"""
    asset: str = Field(..., description="Activo a operar (BTC, ETH, SOL)")
    timeframe: str = Field(default="4h", description="Temporalidad (1h, 4h, 1d)")
    duration: str = Field(default="24h", description="Duración esperada del trade")
    leverage: Optional[float] = Field(default=1.0, description="Apalancamiento")

class ConfigRequest(BaseModel):
    """Modelo para configuración de parámetros"""
    stoploss_percent: Optional[float] = Field(default=None, description="Stop loss en %")
    takeprofit_percent: Optional[float] = Field(default=None, description="Take profit en %")
    max_trades: Optional[int] = Field(default=None, description="Máximo de trades concurrentes")


@app.on_event("startup")
async def startup_event():
    """Inicializa todos los componentes del bot al arrancar"""
    print("🚀 Iniciando SemáforoBot...")
    
    try:
        # Inicializar Redis Store (opcional - modo degradado sin Redis)
        # Prioridad: REDIS_URL (Render/Railway) > REDIS_HOST/PORT (local) > Sin Redis
        redis_connected = False
        redis_url = os.getenv('REDIS_URL')
        
        try:
            if redis_url:
                # Validar esquema: redis://, rediss:// o unix://
                from urllib.parse import urlparse
                parsed = urlparse(redis_url)
                if parsed.scheme in ("redis", "rediss", "unix"):
                    bot_state.redis_store = RedisStore(url=redis_url)
                    print("🔗 Usando REDIS_URL de entorno")
                else:
                    # Si la variable apunta a otro servicio (ej. postgresql), ignorarla
                    print(f"⚠️ REDIS_URL tiene esquema '{parsed.scheme}://' (no es redis://)")
                    print("   Intentando localhost:6379...")
                    bot_state.redis_store = RedisStore(
                        host=os.getenv('REDIS_HOST', 'localhost'),
                        port=int(os.getenv('REDIS_PORT', 6379)),
                        db=int(os.getenv('REDIS_DB', 0))
                    )
            else:
                bot_state.redis_store = RedisStore(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=int(os.getenv('REDIS_DB', 0))
                )
                print("🔗 Intentando Redis en localhost:6379")
            
            await bot_state.redis_store.connect()
            redis_connected = True
            print("✅ Redis conectado")
            
        except Exception as redis_error:
            print(f"⚠️ Redis no disponible: {redis_error}")
            print("⚠️ El bot continuará SIN PERSISTENCIA (memoria volátil)")
            print("   → Los datos se perderán al reiniciar el servicio")
            print("   → Para persistencia, configura Redis externo (Upstash gratis)")
            bot_state.redis_store = None
        
        # Inicializar adaptador de datos (Exchange directo - SIN CoinGlass)
        # Lista de exchanges alternativos si Binance falla (451 en Render)
        exchange_fallbacks = ['binance', 'bybit', 'okx', 'kraken']
        exchange_initialized = False
        
        try:
            primary_exchange = os.getenv('EXCHANGE_NAME', 'binance')
            
            # Intentar con el exchange configurado primero
            for exchange_name in [primary_exchange] + [e for e in exchange_fallbacks if e != primary_exchange]:
                try:
                    print(f"🔄 Intentando conectar a {exchange_name}...")
                    bot_state.data_adapter = ExchangeAdapter(
                        exchange_name=exchange_name,
                        api_key=os.getenv('EXCHANGE_API_KEY'),  # Opcional
                        api_secret=os.getenv('EXCHANGE_API_SECRET')  # Opcional
                    )
                    await bot_state.data_adapter.initialize()
                    print(f"✅ Exchange adapter inicializado ({exchange_name})")
                    exchange_initialized = True
                    break
                except Exception as ex:
                    print(f"⚠️ {exchange_name} falló: {ex}")
                    if "451" in str(ex) or "restricted location" in str(ex).lower():
                        print(f"   → {exchange_name} bloqueado por ubicación, probando alternativa...")
                    continue
            
            if not exchange_initialized:
                print("❌ Ningún exchange disponible")
                print("   El bot continuará con funcionalidad limitada")
        except Exception as e:
            print(f"⚠️ Error inicializando exchanges: {e}")
            print("   El bot continuará con funcionalidad limitada")
        
        # Inicializar analizador de riesgo
        try:
            bot_state.risk_analyzer = RiskAnalyzer(
                config=CONFIG,
                data_adapter=bot_state.data_adapter
            )
            print("✅ Risk analyzer listo")
        except Exception as e:
            print(f"⚠️ Risk analyzer falló: {e}")
        
        # Inicializar optimizador de entradas
        try:
            bot_state.entry_optimizer = EntryOptimizer(
                config=CONFIG,
                data_adapter=bot_state.data_adapter
            )
            print("✅ Entry optimizer listo")
        except Exception as e:
            print(f"⚠️ Entry optimizer falló: {e}")
        
        # Inicializar gestor de memoria
        try:
            bot_state.memory_manager = MemoryManager(
                redis_store=bot_state.redis_store,
                config=CONFIG
            )
            print("✅ Memory manager listo")
        except Exception as e:
            print(f"⚠️ Memory manager falló: {e}")
        
        # Cargar trades activos desde memoria
        try:
            if bot_state.memory_manager:
                bot_state.active_trades = await bot_state.memory_manager.load_active_trades()
                print(f"✅ Trades activos cargados: {len(bot_state.active_trades)}")
        except Exception as e:
            print(f"⚠️ No se pudieron cargar trades: {e}")
        
        print("🎯 SemáforoBot iniciado (algunos componentes pueden no estar disponibles)")
        
    except Exception as e:
        print(f"❌ Error crítico al iniciar: {e}")
        print("⚠️ El servidor continuará pero con funcionalidad muy limitada")
        # NO hacer raise - dejar que el servidor arranque


@app.on_event("shutdown")
async def shutdown_event():
    """Limpieza al cerrar el bot"""
    print("🛑 Deteniendo SemáforoBot...")
    
    if bot_state.data_adapter:
        await bot_state.data_adapter.close()
        print("✅ Exchange desconectado")
    
    if bot_state.redis_store:
        await bot_state.redis_store.disconnect()
        print("✅ Redis desconectado")


@app.get("/", response_class=FileResponse)
async def root():
    """Sirve la interfaz web principal"""
    return FileResponse("static/index_pro.html")


@app.get("/favicon.png", response_class=FileResponse)
async def favicon():
    """Sirve el favicon desde la carpeta static"""
    return FileResponse("static/favicon.png")


@app.get("/status")
async def health_check():
    """
    Health check endpoint para Render y otros servicios
    Siempre retorna 200 si el servidor está vivo
    """
    components_status = {
        "redis": bot_state.redis_store is not None,
        "exchange": bot_state.data_adapter is not None,
        "risk_analyzer": bot_state.risk_analyzer is not None,
        "entry_optimizer": bot_state.entry_optimizer is not None,
        "memory_manager": bot_state.memory_manager is not None
    }
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "components": components_status,
        "healthy_components": sum(components_status.values()),
        "total_components": len(components_status)
    }


@app.get("/api/info")
async def api_info():
    """Endpoint de información del bot (antes estaba en /)"""
    return {
        "bot": CONFIG['project_name'],
        "version": CONFIG['version'],
        "status": "running",
        "active_trades": len(bot_state.active_trades),
        "pending_trade": bot_state.pending_trade is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/analyze")
async def analyze_semaforo(request: AnalyzeRequest):
    """
    Comando: semaforo
    Ejecuta análisis completo de riesgo y devuelve color del semáforo
    """
    try:
        # Determinar activos a analizar
        assets = request.assets or CONFIG['trading_params'].get('default_assets', 'BTC,ETH,SOL').split(',')
        
        # Ejecutar análisis para cada activo
        results = {}
        for asset in assets:
            asset = asset.strip().upper()
            
            # Realizar análisis de riesgo
            analysis = await bot_state.risk_analyzer.analyze(
                asset=asset,
                force_refresh=request.force_refresh
            )
            
            results[asset] = analysis
        
        # Determinar semáforo global (el peor de todos)
        global_color = determine_global_semaforo(results)
        
        # Guardar en memoria
        await bot_state.memory_manager.save_analysis(results)
        
        return {
            "semaforo": global_color,
            "emoji": get_semaforo_emoji(global_color),
            "timestamp": datetime.now().isoformat(),
            "assets": results,
            "recommendation": get_recommendation(global_color)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en análisis: {str(e)}")


@app.post("/trade")
async def prepare_trade(request: TradeRequest):
    """
    Comando: operar [ASSET] [TIMEFRAME] [DURATION]
    Calcula puntos óptimos de entrada/salida según temporalidad
    """
    try:
        asset = request.asset.upper()
        
        # Verificar que el activo esté configurado
        if asset not in CONFIG['assets']:
            raise HTTPException(status_code=400, detail=f"Activo {asset} no configurado")
        
        # Obtener último análisis de semáforo
        last_analysis = await bot_state.memory_manager.get_last_analysis(asset)
        if not last_analysis:
            raise HTTPException(
                status_code=400, 
                detail="No hay análisis previo. Ejecuta 'semaforo' primero"
            )
        
        # Calcular entrada óptima
        entry_data = await bot_state.entry_optimizer.calculate_entry(
            asset=asset,
            timeframe=request.timeframe,
            duration=request.duration,
            risk_analysis=last_analysis,
            leverage=request.leverage
        )
        
        # Guardar trade pendiente
        bot_state.pending_trade = {
            "asset": asset,
            "timeframe": request.timeframe,
            "duration": request.duration,
            "entry_price": entry_data['entry_price'],
            "stoploss": entry_data['stoploss'],
            "takeprofit": entry_data['takeprofit'],
            "direction": entry_data['direction'],
            "confidence": entry_data['confidence'],
            "risk_color": last_analysis.get('color', 'yellow'),
            "timestamp": datetime.now().isoformat()
        }
        
        # Guardar en memoria
        await bot_state.memory_manager.save_pending_trade(bot_state.pending_trade)
        
        return {
            "status": "pending_confirmation",
            "trade": bot_state.pending_trade,
            "message": f"Entrada ideal en {entry_data['entry_price']}, SL {entry_data['stoploss_percent']}%, TP {entry_data['takeprofit_percent']}%. ¿Confirmar trade?"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculando trade: {str(e)}")


@app.post("/confirm")
async def confirm_trade():
    """
    Comando: confirmar trade
    Ejecuta el trade pendiente y lo guarda en memoria activa
    """
    try:
        if not bot_state.pending_trade:
            raise HTTPException(status_code=400, detail="No hay trade pendiente para confirmar")
        
        # Verificar máximo de trades concurrentes
        max_trades = CONFIG['trading_params']['max_concurrent_trades']
        if len(bot_state.active_trades) >= max_trades:
            raise HTTPException(
                status_code=400, 
                detail=f"Máximo de trades concurrentes alcanzado ({max_trades})"
            )
        
        # Generar ID único para el trade
        trade_id = f"{bot_state.pending_trade['asset']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Mover a trades activos
        trade_data = {**bot_state.pending_trade, "trade_id": trade_id, "status": "open"}
        bot_state.active_trades[trade_id] = trade_data
        
        # Guardar en Redis
        await bot_state.memory_manager.save_active_trade(trade_id, trade_data)
        
        # Limpiar pending
        bot_state.pending_trade = None
        await bot_state.memory_manager.clear_pending_trade()
        
        return {
            "status": "confirmed",
            "trade_id": trade_id,
            "trade": trade_data,
            "message": f"Trade abierto. Guardado en memoria. Te avisaré si hay señal de cierre."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error confirmando trade: {str(e)}")


@app.get("/trades/active")
async def get_active_trades():
    """Obtiene lista de trades activos"""
    return {
        "count": len(bot_state.active_trades),
        "trades": bot_state.active_trades
    }


@app.get("/api/price/{symbol}")
async def get_current_price(symbol: str):
    """Obtiene el precio actual de un asset desde Binance"""
    try:
        # Convertir símbolo a formato Binance (BTC -> BTCUSDT)
        binance_symbol = f"{symbol}USDT"
        
        # Obtener precio desde el exchange usando el data_adapter
        ticker = await bot_state.data_adapter.exchange.fetch_ticker(binance_symbol)
        
        return {
            "symbol": symbol,
            "price": ticker['last'],
            "bid": ticker['bid'],
            "ask": ticker['ask'],
            "timestamp": ticker['timestamp']
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo precio de {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo precio: {str(e)}")


@app.post("/trades/{trade_id}/close")
async def close_trade(trade_id: str):
    """Cierra un trade específico"""
    try:
        if trade_id not in bot_state.active_trades:
            raise HTTPException(status_code=404, detail=f"Trade {trade_id} no encontrado")
        
        trade = bot_state.active_trades[trade_id]
        trade['status'] = 'closed'
        trade['close_timestamp'] = datetime.now().isoformat()
        
        # Mover a histórico
        await bot_state.memory_manager.move_to_history(trade_id, trade)
        
        # Eliminar de activos
        del bot_state.active_trades[trade_id]
        
        return {
            "status": "closed",
            "trade_id": trade_id,
            "message": f"Trade {trade_id} cerrado correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cerrando trade: {str(e)}")


@app.post("/config")
async def update_config(request: ConfigRequest):
    """
    Comando: configurar stoploss [%] tp [%]
    Actualiza parámetros de riesgo dinámicamente
    """
    try:
        updates = {}
        
        if request.stoploss_percent is not None:
            CONFIG['trading_params']['default_stoploss_percent'] = request.stoploss_percent
            updates['stoploss'] = request.stoploss_percent
        
        if request.takeprofit_percent is not None:
            CONFIG['trading_params']['default_takeprofit_percent'] = request.takeprofit_percent
            updates['takeprofit'] = request.takeprofit_percent
        
        if request.max_trades is not None:
            CONFIG['trading_params']['max_concurrent_trades'] = request.max_trades
            updates['max_trades'] = request.max_trades
        
        # Guardar configuración actualizada
        await bot_state.memory_manager.save_config_updates(updates)
        
        return {
            "status": "updated",
            "updates": updates,
            "message": "Configuración actualizada correctamente"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando config: {str(e)}")


# Funciones auxiliares
def determine_global_semaforo(results: Dict) -> str:
    """Determina el color global del semáforo basado en todos los análisis"""
    colors = [r.get('color', 'yellow') for r in results.values()]
    
    if 'red' in colors:
        return 'red'
    elif 'yellow' in colors:
        return 'yellow'
    else:
        return 'green'


def get_semaforo_emoji(color: str) -> str:
    """Devuelve el emoji correspondiente al color del semáforo"""
    emojis = {
        'green': '🟢',
        'yellow': '🟡',
        'red': '🔴'
    }
    return emojis.get(color, '⚪')


def get_recommendation(color: str) -> str:
    """Devuelve recomendación según color del semáforo"""
    recommendations = {
        'green': 'Condiciones favorables para operar. Riesgo bajo.',
        'yellow': 'Riesgo medio. Esperar confirmación o entrada moderada.',
        'red': 'Alto riesgo. No se recomienda operar o usar tamaño reducido.'
    }
    return recommendations.get(color, 'Análisis no disponible')


if __name__ == "__main__":
    # Configuración del servidor
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    debug = os.getenv('DEBUG_MODE', 'true').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════╗
    ║       🚦 SemáforoBot v{CONFIG['version']}       ║
    ║  Bot de Trading con Análisis IA      ║
    ╚══════════════════════════════════════╝
    
    🌐 API: http://{host}:{port}
    📚 Docs: http://{host}:{port}/docs
    🔧 Debug: {debug}
    """)
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )
