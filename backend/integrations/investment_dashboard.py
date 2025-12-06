"""
ARIN Platform - Investment Dashboard Integration
Интеграция с Investment Dashboard для получения фундаментальных данных и SEC EDGAR
"""
import logging
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime, timedelta
import pandas as pd

from backend.config import settings

logger = logging.getLogger(__name__)


class InvestmentDashboardClient:
    """
    Клиент для интеграции с Investment Dashboard
    
    Получает:
    - Фундаментальные данные компаний
    - SEC EDGAR данные (10-K, 10-Q, 8-K)
    - Финансовые метрики
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Инициализация клиента
        
        Args:
            base_url: URL Investment Dashboard
        """
        self.base_url = base_url or settings.investment_dashboard_url
        self.enabled = self.base_url is not None
        
        if self.enabled:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=60.0  # Больше таймаут для EDGAR данных
            )
            logger.info(f"Investment Dashboard client initialized: {self.base_url}")
        else:
            logger.info("Investment Dashboard integration disabled (URL not configured)")
            
    async def is_available(self) -> bool:
        """Проверка доступности Investment Dashboard"""
        if not self.enabled:
            return False
            
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Investment Dashboard not available: {e}")
            return False
            
    async def get_fundamental_data(
        self,
        ticker: str,
        period: str = "annual"
    ) -> Optional[Dict[str, Any]]:
        """
        Получение фундаментальных данных компании
        
        Args:
            ticker: Тикер компании (например, "AAPL")
            period: Период (annual, quarterly)
            
        Returns:
            Фундаментальные данные или None
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.get(
                f"/api/v1/fundamentals/{ticker}",
                params={"period": period}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get fundamental data: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting fundamental data: {e}")
            return None
            
    async def get_financial_statements(
        self,
        ticker: str,
        statement_type: str = "income_statement",
        period: str = "annual"
    ) -> Optional[pd.DataFrame]:
        """
        Получение финансовых отчетов
        
        Args:
            ticker: Тикер компании
            statement_type: Тип отчета (income_statement, balance_sheet, cash_flow)
            period: Период (annual, quarterly)
            
        Returns:
            DataFrame с финансовыми данными или None
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.get(
                f"/api/v1/financials/{ticker}/{statement_type}",
                params={"period": period}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Преобразование в DataFrame
                if "data" in data:
                    return pd.DataFrame(data["data"])
                return None
            else:
                logger.warning(f"Failed to get financial statements: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting financial statements: {e}")
            return None
            
    async def get_sec_filings(
        self,
        ticker: str,
        filing_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Получение SEC EDGAR filings
        
        Args:
            ticker: Тикер компании
            filing_type: Тип filing (10-K, 10-Q, 8-K, etc.)
            start_date: Начальная дата
            end_date: Конечная дата
            limit: Лимит результатов
            
        Returns:
            Список filings
        """
        if not await self.is_available():
            return []
            
        try:
            params = {"limit": limit}
            if filing_type:
                params["filing_type"] = filing_type
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()
                
            response = await self.client.get(
                f"/api/v1/sec/filings/{ticker}",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("filings", [])
            else:
                logger.warning(f"Failed to get SEC filings: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting SEC filings: {e}")
            return []
            
    async def get_sec_filing_content(
        self,
        filing_id: str
    ) -> Optional[str]:
        """
        Получение содержимого SEC filing
        
        Args:
            filing_id: ID filing
            
        Returns:
            Текст filing или None
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.get(
                f"/api/v1/sec/filings/{filing_id}/content"
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "")
            else:
                logger.warning(f"Failed to get filing content: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting filing content: {e}")
            return None
            
    async def get_key_metrics(
        self,
        ticker: str
    ) -> Optional[Dict[str, Any]]:
        """
        Получение ключевых метрик компании
        
        Args:
            ticker: Тикер компании
            
        Returns:
            Ключевые метрики или None
        """
        if not await self.is_available():
            return None
            
        try:
            response = await self.client.get(
                f"/api/v1/metrics/{ticker}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get key metrics: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting key metrics: {e}")
            return None
            
    async def search_companies(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Поиск компаний
        
        Args:
            query: Поисковый запрос
            limit: Лимит результатов
            
        Returns:
            Список компаний
        """
        if not await self.is_available():
            return []
            
        try:
            response = await self.client.get(
                "/api/v1/search/companies",
                params={"query": query, "limit": limit}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("companies", [])
            else:
                logger.warning(f"Failed to search companies: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            return []
            
    async def close(self):
        """Закрытие клиента"""
        if self.enabled:
            await self.client.aclose()

