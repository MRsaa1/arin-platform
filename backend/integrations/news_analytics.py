"""
ARIN Platform - News Analytics Integration
Опциональная интеграция с News Analytics Portal
"""
import logging
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime, timedelta

from backend.config import settings

logger = logging.getLogger(__name__)


class NewsAnalyticsClient:
    """
    Клиент для интеграции с News Analytics Portal
    
    Это опциональная интеграция - ARIN может работать без нее
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Инициализация клиента
        
        Args:
            base_url: URL News Analytics Portal
        """
        self.base_url = base_url or settings.news_analytics_url
        self.enabled = self.base_url is not None
        
        if self.enabled:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
            logger.info(f"News Analytics client initialized: {self.base_url}")
        else:
            logger.info("News Analytics integration disabled (URL not configured)")
            
    async def is_available(self) -> bool:
        """
        Проверка доступности News Analytics
        
        Returns:
            True если доступен, False иначе
        """
        if not self.enabled:
            return False
            
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"News Analytics not available: {e}")
            return False
            
    async def get_news(
        self,
        entity_id: Optional[str] = None,
        sector: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Получение новостей
        
        Args:
            entity_id: ID сущности
            sector: Сектор
            start_date: Начальная дата
            end_date: Конечная дата
            limit: Лимит результатов
            
        Returns:
            Список новостей
        """
        if not await self.is_available():
            return []
            
        try:
            params = {"limit": limit}
            if entity_id:
                params["entity_id"] = entity_id
            if sector:
                params["sector"] = sector
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
                
            response = await self.client.get(
                "/api/v1/news",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("news", [])
            else:
                logger.warning(f"Failed to get news: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting news from News Analytics: {e}")
            return []
            
    async def get_sentiment(
        self,
        entity_id: str,
        days: int = 7
    ) -> Optional[Dict[str, Any]]:
        """
        Получение сентимента для сущности
        
        Args:
            entity_id: ID сущности
            days: Количество дней для анализа
            
        Returns:
            Анализ сентимента или None
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.get(
                f"/api/v1/sentiment/{entity_id}",
                params={"days": days}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get sentiment: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting sentiment from News Analytics: {e}")
            return None
            
    async def get_entity_relationships(
        self,
        entity_id: str
    ) -> List[Dict[str, Any]]:
        """
        Получение связей сущности на основе новостей
        
        Args:
            entity_id: ID сущности
            
        Returns:
            Список связанных сущностей
        """
        if not await self.is_available():
            return []
            
        try:
            response = await self.client.get(
                f"/api/v1/relationships/{entity_id}"
            )
            
            if response.status_code == 200:
                return response.json().get("relationships", [])
            else:
                logger.warning(f"Failed to get relationships: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting relationships from News Analytics: {e}")
            return []
            
    async def close(self):
        """Закрытие клиента"""
        if self.enabled:
            await self.client.aclose()

