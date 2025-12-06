"""
ARIN Platform - Cache Service
Redis кэширование для оптимизации производительности
"""
import logging
from typing import Any, Optional
import json
import pickle
from datetime import timedelta
import redis.asyncio as aioredis

from backend.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Сервис кэширования на основе Redis
    
    Поддерживает:
    - Кэширование результатов запросов
    - Кэширование результатов анализа агентов
    - Кэширование графа зависимостей
    - TTL для автоматического истечения
    """
    
    def __init__(self):
        """Инициализация Cache Service"""
        self.redis_client: Optional[aioredis.Redis] = None
        self.enabled = False
        
    async def initialize(self):
        """Инициализация Redis клиента"""
        try:
            self.redis_client = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=False,  # Для pickle
                max_connections=50
            )
            
            # Проверка подключения
            await self.redis_client.ping()
            self.enabled = True
            
            logger.info(f"Cache service initialized: {settings.redis_url}")
            
        except Exception as e:
            logger.warning(f"Redis not available, caching disabled: {e}")
            self.enabled = False
            self.redis_client = None
            
    async def get(
        self,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Получение значения из кэша
        
        Args:
            key: Ключ кэша
            default: Значение по умолчанию
            
        Returns:
            Значение из кэша или default
        """
        if not self.enabled:
            return default
            
        try:
            data = await self.redis_client.get(key)
            if data:
                return pickle.loads(data)
            return default
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return default
            
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Установка значения в кэш
        
        Args:
            key: Ключ кэша
            value: Значение для кэширования
            ttl: Time to live в секундах (если None, без истечения)
            
        Returns:
            True если успешно
        """
        if not self.enabled:
            return False
            
        try:
            data = pickle.dumps(value)
            if ttl:
                await self.redis_client.setex(key, ttl, data)
            else:
                await self.redis_client.set(key, data)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Удаление ключа из кэша"""
        if not self.enabled:
            return False
            
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False
            
    async def delete_pattern(self, pattern: str) -> int:
        """
        Удаление ключей по паттерну
        
        Args:
            pattern: Паттерн для поиска (например, "agent:*")
            
        Returns:
            Количество удаленных ключей
        """
        if not self.enabled:
            return 0
            
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern failed for {pattern}: {e}")
            return 0
            
    async def get_or_set(
        self,
        key: str,
        callable_func,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Получение из кэша или вычисление и сохранение
        
        Args:
            key: Ключ кэша
            callable_func: Функция для вычисления значения (async)
            ttl: Time to live в секундах
            
        Returns:
            Значение из кэша или результат функции
        """
        # Попытка получить из кэша
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Вычисление значения
        value = await callable_func()
        
        # Сохранение в кэш
        await self.set(key, value, ttl)
        
        return value
        
    async def clear_all(self) -> bool:
        """Очистка всего кэша"""
        if not self.enabled:
            return False
            
        try:
            await self.redis_client.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
            
    async def get_stats(self) -> dict:
        """Получение статистики кэша"""
        if not self.enabled:
            return {"enabled": False}
            
        try:
            info = await self.redis_client.info("stats")
            return {
                "enabled": True,
                "keys": await self.redis_client.dbsize(),
                "memory_used": info.get("used_memory_human", "unknown")
            }
        except Exception as e:
            logger.warning(f"Failed to get cache stats: {e}")
            return {"enabled": True, "error": str(e)}
            
    async def shutdown(self):
        """Закрытие соединения с Redis"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Cache service closed")


# Глобальный экземпляр
cache_service = CacheService()

