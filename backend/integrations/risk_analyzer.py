"""
ARIN Platform - Risk Analyzer Integration
Опциональная интеграция с Risk Analyzer Platform
"""
import logging
from typing import Dict, Any, Optional
import httpx
from datetime import datetime, timedelta

from backend.config import settings

logger = logging.getLogger(__name__)


class RiskAnalyzerClient:
    """
    Клиент для интеграции с Risk Analyzer Platform
    
    Это опциональная интеграция - ARIN может работать без нее
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Инициализация клиента
        
        Args:
            base_url: URL Risk Analyzer Platform
        """
        self.base_url = base_url or settings.risk_analyzer_url
        self.enabled = self.base_url is not None
        
        if self.enabled:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
            logger.info(f"Risk Analyzer client initialized: {self.base_url}")
        else:
            logger.info("Risk Analyzer integration disabled (URL not configured)")
            
    async def is_available(self) -> bool:
        """
        Проверка доступности Risk Analyzer
        
        Returns:
            True если доступен, False иначе
        """
        if not self.enabled:
            return False
            
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Risk Analyzer not available: {e}")
            return False
            
    async def get_var_cvar(
        self,
        entity_id: str,
        confidence_level: float = 0.95,
        time_horizon: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Получение VaR/CVaR из Risk Analyzer
        
        Args:
            entity_id: ID сущности
            confidence_level: Уровень доверия
            time_horizon: Временной горизонт (дни)
            
        Returns:
            Результаты VaR/CVaR или None если недоступно
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.post(
                "/api/v1/risks/var-cvar",
                json={
                    "entity_id": entity_id,
                    "confidence_level": confidence_level,
                    "time_horizon": time_horizon
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get VaR/CVaR: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting VaR/CVaR from Risk Analyzer: {e}")
            return None
            
    async def get_historical_data(
        self,
        entity_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Получение исторических данных
        
        Args:
            entity_id: ID сущности
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Исторические данные или None если недоступно
        """
        if not await self.is_available():
            return None
            
        try:
            params = {"entity_id": entity_id}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
                
            response = await self.client.get(
                "/api/v1/data/historical",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get historical data: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting historical data from Risk Analyzer: {e}")
            return None
            
    async def get_stress_test_results(
        self,
        entity_id: str,
        scenarios: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Получение результатов стресс-тестирования
        
        Args:
            entity_id: ID сущности
            scenarios: Список сценариев
            
        Returns:
            Результаты стресс-теста или None если недоступно
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.post(
                "/api/v1/risks/stress-test",
                json={
                    "entity_id": entity_id,
                    "scenarios": scenarios or []
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get stress test results: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting stress test results from Risk Analyzer: {e}")
            return None
            
    async def close(self):
        """Закрытие клиента"""
        if self.enabled:
            await self.client.aclose()

