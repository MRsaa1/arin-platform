"""
ARIN Platform - Crypto Analytics Portal Integration
Интеграция с Crypto Analytics Portal для получения on-chain метрик и exchange данных
"""
import logging
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime, timedelta
import pandas as pd

from backend.config import settings

logger = logging.getLogger(__name__)


class CryptoAnalyticsClient:
    """
    Клиент для интеграции с Crypto Analytics Portal
    
    Получает:
    - On-chain метрики (активные адреса, транзакции, хешрейт)
    - Exchange данные (объемы, цены, order book)
    - DeFi метрики (TVL, ликвидность)
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Инициализация клиента
        
        Args:
            base_url: URL Crypto Analytics Portal
        """
        self.base_url = base_url or settings.crypto_analytics_url
        self.enabled = self.base_url is not None
        
        if self.enabled:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
            logger.info(f"Crypto Analytics client initialized: {self.base_url}")
        else:
            logger.info("Crypto Analytics integration disabled (URL not configured)")
            
    async def is_available(self) -> bool:
        """Проверка доступности Crypto Analytics Portal"""
        if not self.enabled:
            return False
            
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Crypto Analytics not available: {e}")
            return False
            
    async def get_onchain_metrics(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Получение on-chain метрик
        
        Args:
            symbol: Символ криптовалюты (BTC, ETH, etc.)
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            On-chain метрики или None
        """
        if not await self.is_available():
            return None
            
        try:
            params = {}
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
                
            response = await self.client.get(
                f"/api/v1/onchain/{symbol}",
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get on-chain metrics: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting on-chain metrics: {e}")
            return None
            
    async def get_exchange_data(
        self,
        symbol: str,
        exchange: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Получение данных с биржи
        
        Args:
            symbol: Символ криптовалюты
            exchange: Название биржи (если None, агрегированные данные)
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            DataFrame с данными биржи или None
        """
        if not await self.is_available():
            return None
            
        try:
            params = {}
            if exchange:
                params["exchange"] = exchange
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
                
            response = await self.client.get(
                f"/api/v1/exchange/{symbol}",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:
                    return pd.DataFrame(data["data"])
                return None
            else:
                logger.warning(f"Failed to get exchange data: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting exchange data: {e}")
            return None
            
    async def get_orderbook(
        self,
        symbol: str,
        exchange: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получение order book
        
        Args:
            symbol: Символ криптовалюты
            exchange: Название биржи
            
        Returns:
            Order book данные или None
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.get(
                f"/api/v1/orderbook/{exchange}/{symbol}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get orderbook: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting orderbook: {e}")
            return None
            
    async def get_defi_metrics(
        self,
        protocol: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Получение DeFi метрик
        
        Args:
            protocol: Название протокола (если None, агрегированные данные)
            
        Returns:
            DeFi метрики или None
        """
        if not await self.is_available():
            return None
            
        try:
            url = "/api/v1/defi/metrics"
            if protocol:
                url = f"/api/v1/defi/{protocol}/metrics"
                
            response = await self.client.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get DeFi metrics: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting DeFi metrics: {e}")
            return None
            
    async def get_network_stats(
        self,
        symbol: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получение статистики сети
        
        Args:
            symbol: Символ криптовалюты
            
        Returns:
            Статистика сети или None
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.get(
                f"/api/v1/network/{symbol}/stats"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get network stats: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting network stats: {e}")
            return None
            
    async def get_whale_activity(
        self,
        symbol: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Получение активности "китов" (крупных держателей)
        
        Args:
            symbol: Символ криптовалюты
            days: Количество дней для анализа
            
        Returns:
            Список активностей китов
        """
        if not await self.is_available():
            return []
            
        try:
            response = await self.client.get(
                f"/api/v1/whales/{symbol}",
                params={"days": days}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("activities", [])
            else:
                logger.warning(f"Failed to get whale activity: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting whale activity: {e}")
            return []
            
    async def close(self):
        """Закрытие клиента"""
        if self.enabled:
            await self.client.aclose()

