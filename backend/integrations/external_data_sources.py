"""
ARIN Platform - External Data Sources Integration
Интеграция с внешними источниками данных (FRED, ECB, регуляторные базы)
"""
import logging
from typing import Dict, Any, List, Optional
import httpx
from datetime import datetime, timedelta
import pandas as pd

from backend.config import settings

logger = logging.getLogger(__name__)


class FREDClient:
    """
    Клиент для интеграции с FRED (Federal Reserve Economic Data)
    
    Получает макроэкономические данные от Федеральной резервной системы США
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация FRED клиента
        
        Args:
            api_key: FRED API ключ (можно получить на https://fred.stlouisfed.org/docs/api/api_key.html)
        """
        self.api_key = api_key or settings.fred_api_key
        self.base_url = "https://api.stlouisfed.org/fred"
        self.enabled = self.api_key is not None
        
        if self.enabled:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0
            )
            logger.info("FRED client initialized")
        else:
            logger.info("FRED integration disabled (API key not configured)")
            
    async def get_series(
        self,
        series_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[pd.DataFrame]:
        """
        Получение экономического ряда
        
        Args:
            series_id: ID ряда (например, "GDP", "UNRATE", "DGS10")
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            DataFrame с данными или None
        """
        if not self.enabled:
            return None
            
        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json"
            }
            
            if start_date:
                params["observation_start"] = start_date.strftime("%Y-%m-%d")
            if end_date:
                params["observation_end"] = end_date.strftime("%Y-%m-%d")
                
            response = await self.client.get(
                "/series/observations",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                observations = data.get("observations", [])
                
                if observations:
                    df = pd.DataFrame(observations)
                    df["date"] = pd.to_datetime(df["date"])
                    df["value"] = pd.to_numeric(df["value"], errors="coerce")
                    return df
                return None
            else:
                logger.warning(f"Failed to get FRED series: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting FRED series: {e}")
            return None
            
    async def get_macro_indicators(
        self,
        indicators: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Получение нескольких макроэкономических индикаторов
        
        Args:
            indicators: Список ID индикаторов
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Словарь {indicator_id: DataFrame}
        """
        results = {}
        for indicator in indicators:
            results[indicator] = await self.get_series(indicator, start_date, end_date)
        return results


class ECBClient:
    """
    Клиент для интеграции с ECB (European Central Bank)
    
    Получает макроэкономические данные от Европейского центрального банка
    """
    
    def __init__(self):
        """Инициализация ECB клиента"""
        self.base_url = "https://sdw-wsrest.ecb.europa.eu/service"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0
        )
        logger.info("ECB client initialized")
        
    async def get_data(
        self,
        dataflow: str,
        key: Optional[str] = None,
        start_period: Optional[str] = None,
        end_period: Optional[str] = None
    ) -> Optional[pd.DataFrame]:
        """
        Получение данных из ECB
        
        Args:
            dataflow: Идентификатор потока данных
            key: Ключ для фильтрации
            start_period: Начальный период (YYYY-MM-DD)
            end_period: Конечный период (YYYY-MM-DD)
            
        Returns:
            DataFrame с данными или None
        """
        try:
            url = f"/data/{dataflow}"
            params = {}
            
            if key:
                params["key"] = key
            if start_period:
                params["startPeriod"] = start_period
            if end_period:
                params["endPeriod"] = end_period
                
            response = await self.client.get(url, params=params)
            
            if response.status_code == 200:
                # Парсинг XML ответа (ECB использует XML)
                # Упрощенная версия - в production нужен полноценный XML парсер
                logger.info(f"ECB data retrieved for {dataflow}")
                # TODO: Реализовать парсинг XML в DataFrame
                return None
            else:
                logger.warning(f"Failed to get ECB data: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting ECB data: {e}")
            return None


class RegulatoryDatabaseClient:
    """
    Клиент для интеграции с регуляторными базами данных
    
    Поддерживает:
    - SEC EDGAR (через Investment Dashboard)
    - FINRA
    - FCA (UK)
    - ESMA (EU)
    """
    
    def __init__(self):
        """Инициализация клиента"""
        logger.info("Regulatory Database client initialized")
        
    async def search_regulations(
        self,
        jurisdiction: str,
        keywords: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск регуляторных документов
        
        Args:
            jurisdiction: Юрисдикция (US, EU, UK)
            keywords: Ключевые слова для поиска
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Список найденных документов
        """
        # TODO: Реализовать поиск в регуляторных базах
        logger.info(f"Searching regulations in {jurisdiction} for keywords: {keywords}")
        return []
        
    async def get_regulatory_changes(
        self,
        jurisdiction: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Получение изменений в регуляциях
        
        Args:
            jurisdiction: Юрисдикция
            days: Количество дней для поиска
            
        Returns:
            Список изменений
        """
        # TODO: Реализовать получение изменений
        logger.info(f"Getting regulatory changes for {jurisdiction} (last {days} days)")
        return []


class ExternalDataSourcesManager:
    """
    Менеджер для управления всеми внешними источниками данных
    """
    
    def __init__(self):
        """Инициализация менеджера"""
        self.fred_client = FREDClient()
        self.ecb_client = ECBClient()
        self.regulatory_client = RegulatoryDatabaseClient()
        
    async def get_macroeconomic_data(
        self,
        indicators: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Optional[pd.DataFrame]]:
        """
        Получение макроэкономических данных из различных источников
        
        Args:
            indicators: Список индикаторов (с префиксом источника, например "FRED:GDP")
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Словарь {indicator: DataFrame}
        """
        results = {}
        
        for indicator in indicators:
            if indicator.startswith("FRED:"):
                series_id = indicator.replace("FRED:", "")
                results[indicator] = await self.fred_client.get_series(
                    series_id, start_date, end_date
                )
            elif indicator.startswith("ECB:"):
                dataflow = indicator.replace("ECB:", "")
                results[indicator] = await self.ecb_client.get_data(
                    dataflow, start_period=start_date.strftime("%Y-%m-%d") if start_date else None,
                    end_period=end_date.strftime("%Y-%m-%d") if end_date else None
                )
            else:
                logger.warning(f"Unknown indicator source: {indicator}")
                
        return results
        
    async def close(self):
        """Закрытие всех клиентов"""
        if self.fred_client.enabled:
            await self.fred_client.client.aclose()
        await self.ecb_client.client.aclose()

