"""
🎯 API LONG/SHORT - ON-DEMAND SSE (Profesional)
================================================

Sistema inteligente que:
- NO pre-carga datos al inicio
- Solo scrapea la moneda que el usuario solicita
- Actualiza cada 2 segundos mientras el usuario está conectado
- Múltiples clientes pueden ver diferentes monedas simultáneamente
- Usa scraping REAL cada 2 segundos (no cache viejo)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from datetime import datetime
from typing import Dict, Set
import uvicorn
from scrape_coinglass_v6_dropdown import get_coinglass_exact

app = FastAPI(title="SemáforoBot - Long/Short On-Demand SSE")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global: clientes activos por símbolo
active_clients: Dict[str, Set] = {}


class LongShortData(BaseModel):
    symbol: str
    longRatio: float
    shortRatio: float
    timestamp: str
    source: str = "coinglass_5m"


@app.get("/")
async def root():
    """Información de la API"""
    return {
        "api": "SemáforoBot Long/Short On-Demand",
        "version": "2.0",
        "mode": "on-demand",
        "update_interval": "2 seconds",
        "features": [
            "No pre-carga de datos",
            "Solo scrapea la moneda solicitada",
            "Actualización real cada 2 segundos",
            "Scraping bajo demanda"
        ],
        "endpoints": {
            "/longshort/stream/{symbol}": "Stream SSE para una moneda específica",
            "/longshort/{symbol}": "Obtener datos una sola vez (sin stream)"
        }
    }


@app.get("/longshort/{symbol}")
async def get_longshort_once(symbol: str):
    """
    Obtiene datos Long/Short una sola vez (sin streaming).
    Útil para obtener datos iniciales rápidamente.
    """
    try:
        symbol = symbol.upper()
        print(f"📊 Solicitud única para {symbol}...")
        
        data = await get_coinglass_exact(symbol, interval="5m")
        
        if data is None:
            return {"error": f"No se pudieron obtener datos para {symbol}"}
        
        # Convertir al formato SSE
        return LongShortData(
            symbol=symbol,
            longRatio=data["longs_percent"],
            shortRatio=data["shorts_percent"],
            timestamp=data["timestamp"],
            source=data["source"]
        )
        
    except Exception as e:
        return {"error": str(e)}


@app.get("/longshort/stream/{symbol}")
async def stream_longshort(symbol: str):
    """
    Stream SSE que actualiza cada 2 segundos con scraping REAL.
    
    - Comienza inmediatamente (sin pre-carga)
    - Scrapea CoinGlass cada 2 segundos
    - Se detiene automáticamente cuando el cliente se desconecta
    - Múltiples clientes pueden ver diferentes monedas
    """
    symbol = symbol.upper()
    client_id = id(asyncio.current_task())
    
    # Registrar cliente activo
    if symbol not in active_clients:
        active_clients[symbol] = set()
    active_clients[symbol].add(client_id)
    
    print(f"🟢 Cliente conectado para {symbol} (Total: {len(active_clients[symbol])} clientes)")
    
    async def event_generator():
        try:
            # Enviar evento inicial de conexión
            init_event = {
                "symbol": symbol,
                "status": "connected",
                "message": "Iniciando scraping...",
                "timestamp": datetime.now().isoformat()
            }
            yield f"event: connected\n"
            yield f"data: {json.dumps(init_event)}\n\n"
            print(f"🟢 Conexión establecida para {symbol}")
            
            while True:
                try:
                    # Enviar evento de scraping en progreso
                    loading_event = {
                        "symbol": symbol,
                        "status": "scraping",
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"event: loading\n"
                    yield f"data: {json.dumps(loading_event)}\n\n"
                    
                    # 🔥 SCRAPING con TIMEOUT de 30 segundos (aumentado para Render)
                    print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Scraping {symbol}...")
                    
                    try:
                        # Timeout de 30 segundos para el scraping (Render puede ser más lento)
                        data = await asyncio.wait_for(
                            get_coinglass_exact(symbol, interval="5m"),
                            timeout=30.0
                        )
                    except asyncio.TimeoutError:
                        print(f"⏱️ Timeout al scrapear {symbol} (30s)")
                        error_event = {
                            "symbol": symbol,
                            "error": "Timeout scraping CoinGlass (30s) - Render network/CPU may be slow",
                            "timestamp": datetime.now().isoformat()
                        }
                        yield f"event: error\n"
                        yield f"data: {json.dumps(error_event)}\n\n"
                        await asyncio.sleep(5)  # Esperar más antes de reintentar
                        continue
                    except Exception as scrape_error:
                        print(f"❌ Error de scraping para {symbol}: {scrape_error}")
                        error_event = {
                            "symbol": symbol,
                            "error": f"Scraping error: {str(scrape_error)}",
                            "timestamp": datetime.now().isoformat()
                        }
                        yield f"event: error\n"
                        yield f"data: {json.dumps(error_event)}\n\n"
                        await asyncio.sleep(5)
                        continue
                    
                    if data:
                        # Crear evento SSE
                        event_data = LongShortData(
                            symbol=symbol,
                            longRatio=data["longs_percent"],
                            shortRatio=data["shorts_percent"],
                            timestamp=datetime.now().isoformat(),
                            source="coinglass_realtime"
                        )
                        
                        # Enviar como evento SSE
                        yield f"event: update\n"
                        yield f"data: {event_data.model_dump_json()}\n\n"
                        
                        print(f"✅ {symbol}: Long {data['longs_percent']:.2f}% | Short {data['shorts_percent']:.2f}%")
                    
                    else:
                        # Error en scraping
                        error_event = {
                            "symbol": symbol,
                            "error": "No se pudieron obtener datos",
                            "timestamp": datetime.now().isoformat()
                        }
                        yield f"event: error\n"
                        yield f"data: {json.dumps(error_event)}\n\n"
                        print(f"❌ Error al scrapear {symbol}")
                    
                    # Esperar 2 segundos antes del próximo scraping
                    await asyncio.sleep(2)
                    
                except asyncio.CancelledError:
                    print(f"🔴 Stream cancelado para {symbol}")
                    break
                    
                except Exception as e:
                    print(f"⚠️ Error en stream de {symbol}: {e}")
                    error_event = {
                        "symbol": symbol,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"event: error\n"
                    yield f"data: {error_event}\n\n"
                    await asyncio.sleep(2)
                    
        finally:
            # Limpiar cliente al desconectar
            if symbol in active_clients:
                active_clients[symbol].discard(client_id)
                if not active_clients[symbol]:
                    del active_clients[symbol]
                print(f"🔴 Cliente desconectado de {symbol} (Restantes: {len(active_clients.get(symbol, set()))})")
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/status")
async def get_status():
    """Estado del servidor y clientes activos"""
    return {
        "active_symbols": list(active_clients.keys()),
        "total_clients": sum(len(clients) for clients in active_clients.values()),
        "clients_per_symbol": {
            symbol: len(clients) for symbol, clients in active_clients.items()
        },
        "timestamp": datetime.now().isoformat()
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Limpiar recursos al cerrar el servidor"""
    print("\n🛑 Cerrando servidor...")
    print("✅ Recursos liberados")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 LONG/SHORT ON-DEMAND SSE - Modo Profesional")
    print("="*60)
    print()
    print("✅ Sin pre-carga de datos")
    print("✅ Scraping real cada 2 segundos (5min de CoinGlass)")
    print("✅ Solo scrapea la moneda solicitada")
    print("✅ Múltiples clientes soportados")
    print()
    print("🌐 Servidor: http://localhost:8001")
    print("📡 Stream:   http://localhost:8001/longshort/stream/BTC")
    print("📊 Status:   http://localhost:8001/status")
    print()
    print("="*60)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
