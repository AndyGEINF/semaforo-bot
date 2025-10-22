"""
Redis Store Module
Gestión de conexión y operaciones con Redis para persistencia

Operaciones soportadas:
- set/get para datos simples
- sadd/smembers para conjuntos
- Expiración de keys (TTL)
"""

import asyncio
from typing import Optional, Any, Set
import json
import os
import redis.asyncio as redis
from urllib.parse import urlparse


class RedisStore:
    """
    Wrapper para operaciones con Redis de forma asíncrona
    Soporta conexión via URL (ej: redis://user:pass@host:port) o parámetros individuales
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None
    ):
        """
        Inicializa la conexión a Redis
        
        Args:
            url: URL completa de Redis (ej: redis://localhost:6379) - Prioridad sobre host/port
            host: Host de Redis (usado si url=None)
            port: Puerto de Redis (usado si url=None)
            db: Número de base de datos
            password: Contraseña (opcional)
        """
        self.url = url
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Establece conexión con Redis"""
        try:
            # Si hay URL, usarla (para Render, Railway, etc.)
            if self.url:
                self.client = await redis.from_url(
                    self.url,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                print(f"✅ Conectado a Redis via URL")
            else:
                # Conexión tradicional con host/port
                self.client = await redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                print(f"✅ Conectado a Redis en {self.host}:{self.port}")
            
            # Verificar conexión
            await self.client.ping()
            
        except Exception as e:
            print(f"❌ Error conectando a Redis: {e}")
            if self.url:
                print(f"⚠️ URL de Redis: {self.url[:20]}...") # Mostrar solo inicio por seguridad
            else:
                print(f"⚠️ NOTA: Asegúrate de que Redis esté corriendo en {self.host}:{self.port}")
                print(f"   Puedes instalar Redis con: sudo apt install redis-server (Linux)")
                print(f"   O descargar desde: https://redis.io/download")
            raise
    
    async def disconnect(self) -> None:
        """Cierra la conexión con Redis"""
        if self.client:
            await self.client.close()
            print("✅ Desconectado de Redis")
    
    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None
    ) -> bool:
        """
        Guarda un valor en Redis
        
        Args:
            key: Clave
            value: Valor (string o JSON serializado)
            expire: Tiempo de expiración en segundos (opcional)
            
        Returns:
            True si se guardó correctamente
        """
        try:
            if expire:
                await self.client.setex(key, expire, value)
            else:
                await self.client.set(key, value)
            return True
            
        except Exception as e:
            print(f"⚠️ Error guardando en Redis [{key}]: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """
        Obtiene un valor de Redis
        
        Args:
            key: Clave a buscar
            
        Returns:
            Valor guardado o None si no existe
        """
        try:
            return await self.client.get(key)
            
        except Exception as e:
            print(f"⚠️ Error obteniendo de Redis [{key}]: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Elimina una clave de Redis
        
        Args:
            key: Clave a eliminar
            
        Returns:
            True si se eliminó
        """
        try:
            await self.client.delete(key)
            return True
            
        except Exception as e:
            print(f"⚠️ Error eliminando de Redis [{key}]: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe
        
        Args:
            key: Clave a verificar
            
        Returns:
            True si existe
        """
        try:
            return await self.client.exists(key) > 0
            
        except Exception as e:
            print(f"⚠️ Error verificando existencia [{key}]: {e}")
            return False
    
    async def sadd(self, key: str, *values: str) -> int:
        """
        Agrega elementos a un conjunto (set)
        
        Args:
            key: Clave del set
            values: Valores a agregar
            
        Returns:
            Número de elementos agregados
        """
        try:
            return await self.client.sadd(key, *values)
            
        except Exception as e:
            print(f"⚠️ Error agregando a set [{key}]: {e}")
            return 0
    
    async def smembers(self, key: str) -> Set[str]:
        """
        Obtiene todos los miembros de un conjunto
        
        Args:
            key: Clave del set
            
        Returns:
            Set con todos los miembros
        """
        try:
            return await self.client.smembers(key)
            
        except Exception as e:
            print(f"⚠️ Error obteniendo miembros de set [{key}]: {e}")
            return set()
    
    async def srem(self, key: str, *values: str) -> int:
        """
        Elimina elementos de un conjunto
        
        Args:
            key: Clave del set
            values: Valores a eliminar
            
        Returns:
            Número de elementos eliminados
        """
        try:
            return await self.client.srem(key, *values)
            
        except Exception as e:
            print(f"⚠️ Error eliminando de set [{key}]: {e}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Establece tiempo de expiración para una clave
        
        Args:
            key: Clave
            seconds: Segundos hasta expiración
            
        Returns:
            True si se estableció correctamente
        """
        try:
            return await self.client.expire(key, seconds)
            
        except Exception as e:
            print(f"⚠️ Error estableciendo expiración [{key}]: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> list:
        """
        Busca claves que coincidan con un patrón
        
        Args:
            pattern: Patrón de búsqueda (ej: "semaforo:*")
            
        Returns:
            Lista de claves encontradas
        """
        try:
            return await self.client.keys(pattern)
            
        except Exception as e:
            print(f"⚠️ Error buscando keys [{pattern}]: {e}")
            return []
    
    async def flushdb(self) -> bool:
        """
        CUIDADO: Elimina toda la base de datos actual
        
        Returns:
            True si se limpió correctamente
        """
        try:
            await self.client.flushdb()
            print("⚠️ Base de datos Redis limpiada")
            return True
            
        except Exception as e:
            print(f"⚠️ Error limpiando base de datos: {e}")
            return False


# Función de testing
async def test_redis():
    """Función de prueba de Redis"""
    print("🧪 Testing Redis Store...")
    
    store = RedisStore()
    
    try:
        await store.connect()
        
        # Test set/get
        print("\n✅ Test 1: Set/Get")
        await store.set("test:key", "test_value", expire=60)
        value = await store.get("test:key")
        print(f"   Valor guardado: {value}")
        
        # Test set operations
        print("\n✅ Test 2: Set Operations")
        await store.sadd("test:set", "value1", "value2", "value3")
        members = await store.smembers("test:set")
        print(f"   Miembros del set: {members}")
        
        # Test exists
        print("\n✅ Test 3: Exists")
        exists = await store.exists("test:key")
        print(f"   test:key existe: {exists}")
        
        # Cleanup
        await store.delete("test:key")
        await store.delete("test:set")
        
        print("\n✅ Todos los tests pasaron!")
        
    except Exception as e:
        print(f"\n❌ Test falló: {e}")
        
    finally:
        await store.disconnect()


if __name__ == "__main__":
    # Ejecutar test
    asyncio.run(test_redis())
