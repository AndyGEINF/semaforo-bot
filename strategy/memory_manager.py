"""
Strategy - Memory Manager Module
Gestiona la memoria persistente de análisis, trades y configuración

Funciones:
- Guardar/cargar análisis de riesgo
- Gestionar trades activos y pendientes
- Mantener historial de trades
- Recordar configuración personalizada
"""

import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta


class MemoryManager:
    """
    Gestor de memoria que mantiene el estado del bot y permite
    recuperar contexto de sesiones anteriores
    """
    
    def __init__(self, redis_store, config: Dict):
        """
        Inicializa el gestor de memoria
        
        Args:
            redis_store: Instancia de RedisStore
            config: Configuración del sistema
        """
        self.redis = redis_store
        self.config = config
        self.memory_config = config['memory']
        
        # Keys de Redis
        self.ANALYSIS_KEY = "semaforo:analysis:{asset}"
        self.PENDING_TRADE_KEY = "semaforo:pending_trade"
        self.ACTIVE_TRADES_KEY = "semaforo:active_trades"
        self.TRADE_HISTORY_KEY = "semaforo:trade_history"
        self.CONFIG_UPDATES_KEY = "semaforo:config_updates"
    
    async def save_analysis(self, analysis_results: Dict) -> None:
        """
        Guarda análisis de riesgo en memoria
        
        Args:
            analysis_results: Dict con análisis por activo
        """
        try:
            ttl_seconds = self.memory_config['analysis_cache_minutes'] * 60
            
            for asset, data in analysis_results.items():
                key = self.ANALYSIS_KEY.format(asset=asset)
                await self.redis.set(
                    key,
                    json.dumps(data),
                    expire=ttl_seconds
                )
                
        except Exception as e:
            print(f"⚠️ Error guardando análisis: {e}")
    
    async def get_last_analysis(self, asset: str) -> Optional[Dict]:
        """
        Obtiene último análisis guardado para un activo
        
        Args:
            asset: Símbolo del activo
            
        Returns:
            Dict con análisis o None si no existe
        """
        try:
            key = self.ANALYSIS_KEY.format(asset=asset)
            data = await self.redis.get(key)
            
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            print(f"⚠️ Error obteniendo análisis: {e}")
            return None
    
    async def save_pending_trade(self, trade_data: Dict) -> None:
        """
        Guarda trade pendiente de confirmación
        
        Args:
            trade_data: Datos del trade pendiente
        """
        try:
            await self.redis.set(
                self.PENDING_TRADE_KEY,
                json.dumps(trade_data),
                expire=3600  # 1 hora
            )
            
        except Exception as e:
            print(f"⚠️ Error guardando trade pendiente: {e}")
    
    async def get_pending_trade(self) -> Optional[Dict]:
        """
        Obtiene trade pendiente de confirmación
        
        Returns:
            Dict con trade pendiente o None
        """
        try:
            data = await self.redis.get(self.PENDING_TRADE_KEY)
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            print(f"⚠️ Error obteniendo trade pendiente: {e}")
            return None
    
    async def clear_pending_trade(self) -> None:
        """Elimina el trade pendiente"""
        try:
            await self.redis.delete(self.PENDING_TRADE_KEY)
        except Exception as e:
            print(f"⚠️ Error limpiando trade pendiente: {e}")
    
    async def save_active_trade(self, trade_id: str, trade_data: Dict) -> None:
        """
        Guarda un trade activo
        
        Args:
            trade_id: ID único del trade
            trade_data: Datos completos del trade
        """
        try:
            # Guardar trade individual
            trade_key = f"{self.ACTIVE_TRADES_KEY}:{trade_id}"
            await self.redis.set(
                trade_key,
                json.dumps(trade_data),
                expire=None  # Sin expiración para trades activos
            )
            
            # Agregar a lista de trades activos
            await self.redis.sadd(self.ACTIVE_TRADES_KEY, trade_id)
            
        except Exception as e:
            print(f"⚠️ Error guardando trade activo: {e}")
    
    async def load_active_trades(self) -> Dict[str, Dict]:
        """
        Carga todos los trades activos
        
        Returns:
            Dict con trade_id como key y datos como value
        """
        try:
            # Obtener lista de IDs de trades activos
            trade_ids = await self.redis.smembers(self.ACTIVE_TRADES_KEY)
            
            if not trade_ids:
                return {}
            
            # Cargar datos de cada trade
            trades = {}
            for trade_id in trade_ids:
                trade_key = f"{self.ACTIVE_TRADES_KEY}:{trade_id}"
                data = await self.redis.get(trade_key)
                
                if data:
                    trades[trade_id] = json.loads(data)
            
            return trades
            
        except Exception as e:
            print(f"⚠️ Error cargando trades activos: {e}")
            return {}
    
    async def move_to_history(self, trade_id: str, trade_data: Dict) -> None:
        """
        Mueve un trade cerrado al historial
        
        Args:
            trade_id: ID del trade
            trade_data: Datos completos del trade cerrado
        """
        try:
            # Agregar a historial
            history_key = f"{self.TRADE_HISTORY_KEY}:{trade_id}"
            ttl_days = self.memory_config['trade_history_days']
            await self.redis.set(
                history_key,
                json.dumps(trade_data),
                expire=ttl_days * 86400  # Días a segundos
            )
            
            # Eliminar de activos
            trade_key = f"{self.ACTIVE_TRADES_KEY}:{trade_id}"
            await self.redis.delete(trade_key)
            await self.redis.srem(self.ACTIVE_TRADES_KEY, trade_id)
            
        except Exception as e:
            print(f"⚠️ Error moviendo trade a historial: {e}")
    
    async def get_trade_history(self, limit: int = 10) -> List[Dict]:
        """
        Obtiene historial de trades
        
        Args:
            limit: Número máximo de trades a retornar
            
        Returns:
            Lista de trades históricos
        """
        try:
            # TODO: Implementar búsqueda de historial
            # Por ahora, retornar lista vacía
            return []
            
        except Exception as e:
            print(f"⚠️ Error obteniendo historial: {e}")
            return []
    
    async def save_config_updates(self, updates: Dict) -> None:
        """
        Guarda actualizaciones de configuración
        
        Args:
            updates: Dict con parámetros actualizados
        """
        try:
            # Obtener configuración actual
            current = await self.redis.get(self.CONFIG_UPDATES_KEY)
            if current:
                config_data = json.loads(current)
            else:
                config_data = {}
            
            # Actualizar con nuevos valores
            config_data.update(updates)
            config_data['last_update'] = datetime.now().isoformat()
            
            # Guardar
            await self.redis.set(
                self.CONFIG_UPDATES_KEY,
                json.dumps(config_data)
            )
            
        except Exception as e:
            print(f"⚠️ Error guardando configuración: {e}")
    
    async def get_config_updates(self) -> Dict:
        """
        Obtiene configuración personalizada guardada
        
        Returns:
            Dict con configuración o dict vacío
        """
        try:
            data = await self.redis.get(self.CONFIG_UPDATES_KEY)
            if data:
                return json.loads(data)
            return {}
            
        except Exception as e:
            print(f"⚠️ Error obteniendo configuración: {e}")
            return {}
    
    async def get_session_context(self) -> Dict:
        """
        Obtiene contexto completo de la sesión actual
        
        Returns:
            Dict con todo el contexto: análisis, trades, config
        """
        try:
            context = {
                'active_trades': await self.load_active_trades(),
                'pending_trade': await self.get_pending_trade(),
                'config_updates': await self.get_config_updates(),
                'timestamp': datetime.now().isoformat()
            }
            
            return context
            
        except Exception as e:
            print(f"⚠️ Error obteniendo contexto: {e}")
            return {}
