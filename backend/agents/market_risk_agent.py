"""
ARIN Platform - Market Risk Agent
Агент для анализа рыночного риска
"""
import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy.stats import norm

from backend.agents.base_agent import BaseAgent, AgentStatus
from backend.config import settings

logger = logging.getLogger(__name__)


class MarketRiskAgent(BaseAgent):
    """Агент для анализа рыночного риска"""
    
    def __init__(self, agent_id: str = "market_risk_agent", config: Optional[Dict[str, Any]] = None):
        """
        Инициализация Market Risk Agent
        
        Args:
            agent_id: ID агента
            config: Конфигурация агента
        """
        if config is None:
            config = {}
            
        super().__init__(
            agent_id=agent_id,
            agent_name="Market Risk Agent",
            config=config
        )
        
        self.db_engine = None
        self.risk_analyzer_client = None
        
    async def _setup_data_access(self):
        """Настройка доступа к данным"""
        try:
            # TODO: Настроить подключение к БД
            # from sqlalchemy import create_engine
            # self.db_engine = create_engine(settings.database_url)
            
            # Опциональная интеграция с Risk Analyzer Platform
            if self.config.get("risk_analyzer_url"):
                from backend.integrations.risk_analyzer import RiskAnalyzerClient
                self.risk_analyzer_client = RiskAnalyzerClient(
                    self.config.get("risk_analyzer_url")
                )
                logger.info("Risk Analyzer integration available")
            else:
                logger.info("Risk Analyzer integration not configured (optional)")
                
            logger.info("Market Risk Agent data access setup completed")
        except Exception as e:
            logger.error(f"Failed to setup data access: {e}")
            raise
            
    async def _setup_ai_integration(self):
        """Настройка AI интеграции"""
        try:
            # TODO: Настроить LLM клиенты (GPT-4, DeepSeek)
            # if settings.openai_api_key:
            #     self.openai_client = OpenAI(api_key=settings.openai_api_key)
            # if settings.deepseek_api_key:
            #     self.deepseek_client = ...
            
            # TODO: Настроить NVIDIA интеграцию
            # if settings.nvidia_api_key:
            #     self.nvidia_client = ...
            
            logger.info("Market Risk Agent AI integration setup completed")
        except Exception as e:
            logger.error(f"Failed to setup AI integration: {e}")
            raise
            
    async def analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ рыночного риска
        
        Args:
            task: Задача для анализа
                - entity_id: ID сущности (портфель, актив и т.д.)
                - entity_type: Тип сущности
                - parameters: Дополнительные параметры
                
        Returns:
            Результаты анализа рыночного риска
        """
        entity_id = task.get("entity_id")
        entity_type = task.get("entity_type", "portfolio")
        parameters = task.get("parameters", {})
        
        logger.info(f"Analyzing market risk for {entity_type} {entity_id}")
        
        try:
            # 1. Получение рыночных данных
            market_data = await self._get_market_data(entity_id, entity_type)
            
            # 2. Расчет VaR/CVaR
            var_results = await self._calculate_var_cvar(market_data, parameters)
            
            # 3. Стресс-тестирование
            stress_results = await self._stress_test(market_data, parameters)
            
            # 4. Анализ волатильности
            volatility_analysis = await self._analyze_volatility(market_data)
            
            # 5. Анализ корреляций
            correlation_analysis = await self._analyze_correlations(market_data)
            
            # 6. Генерация рекомендаций
            recommendations = await self._generate_recommendations(
                var_results, stress_results, volatility_analysis, correlation_analysis
            )
            
            result = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "timestamp": datetime.now().isoformat(),
                "var_results": var_results,
                "stress_results": stress_results,
                "volatility_analysis": volatility_analysis,
                "correlation_analysis": correlation_analysis,
                "recommendations": recommendations,
                "risk_score": self._calculate_overall_risk_score(
                    var_results, stress_results, volatility_analysis
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze market risk: {e}")
            raise
            
    async def _get_market_data(
        self, 
        entity_id: Optional[str], 
        entity_type: str
    ) -> pd.DataFrame:
        """
        Получение рыночных данных
        
        Args:
            entity_id: ID сущности
            entity_type: Тип сущности
            
        Returns:
            DataFrame с рыночными данными
        """
        # Попытка получить данные из Crypto Analytics Portal (для криптовалют)
        if entity_type == "crypto" and self.config.get("crypto_analytics_url"):
            try:
                from backend.integrations.crypto_analytics import CryptoAnalyticsClient
                crypto_client = CryptoAnalyticsClient(
                    self.config.get("crypto_analytics_url")
                )
                
                exchange_data = await crypto_client.get_exchange_data(
                    symbol=entity_id,
                    start_date=datetime.now() - timedelta(days=365),
                    end_date=datetime.now()
                )
                
                if exchange_data is not None and not exchange_data.empty:
                    logger.info(f"Market data retrieved from Crypto Analytics for {entity_id}")
                    return exchange_data
            except Exception as e:
                logger.warning(f"Failed to get data from Crypto Analytics: {e}")
        
        # Попытка получить данные из Risk Analyzer Platform
        if self.risk_analyzer_client:
            try:
                historical_data = await self.risk_analyzer_client.get_historical_data(
                    entity_id, 
                    start_date=datetime.now() - timedelta(days=365),
                    end_date=datetime.now()
                )
                if historical_data:
                    # Преобразование данных из Risk Analyzer
                    # TODO: Адаптировать под формат данных Risk Analyzer
                    pass
            except Exception as e:
                logger.warning(f"Failed to get data from Risk Analyzer: {e}")
        
        # Fallback: генерация тестовых данных
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * (1 + returns).cumprod()
        
        data = pd.DataFrame({
            'date': dates,
            'price': prices,
            'returns': returns
        })
        
        return data
        
    async def _calculate_var_cvar(
        self, 
        market_data: pd.DataFrame, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Расчет VaR и CVaR
        
        Args:
            market_data: Рыночные данные
            parameters: Параметры расчета (confidence_level, time_horizon)
            
        Returns:
            Результаты расчета VaR/CVaR
        """
        confidence_level = parameters.get("confidence_level", 0.95)
        time_horizon = parameters.get("time_horizon", 1)  # дни
        
        returns = market_data['returns'].values
        
        # Historical VaR
        var_historical = np.percentile(returns, (1 - confidence_level) * 100)
        
        # Parametric VaR (предполагая нормальное распределение)
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        var_parametric = mean_return - norm.ppf(confidence_level) * std_return
        
        # CVaR (Conditional VaR / Expected Shortfall)
        var_threshold = np.percentile(returns, (1 - confidence_level) * 100)
        cvar = np.mean(returns[returns <= var_threshold])
        
        # Масштабирование на временной горизонт
        var_historical_scaled = var_historical * np.sqrt(time_horizon)
        var_parametric_scaled = var_parametric * np.sqrt(time_horizon)
        cvar_scaled = cvar * np.sqrt(time_horizon)
        
        return {
            "var_historical": float(var_historical_scaled),
            "var_parametric": float(var_parametric_scaled),
            "cvar": float(cvar_scaled),
            "confidence_level": confidence_level,
            "time_horizon": time_horizon,
            "method": "historical_and_parametric"
        }
        
    async def _stress_test(
        self, 
        market_data: pd.DataFrame, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Стресс-тестирование
        
        Args:
            market_data: Рыночные данные
            parameters: Параметры стресс-теста
            
        Returns:
            Результаты стресс-тестирования
        """
        returns = market_data['returns'].values
        
        # Сценарии стресс-теста
        scenarios = {
            "market_crash": {
                "shock": -0.20,  # -20% шок
                "description": "Рыночный крах"
            },
            "high_volatility": {
                "shock": 0.05,  # +5% волатильность
                "description": "Высокая волатильность"
            },
            "moderate_decline": {
                "shock": -0.10,  # -10% снижение
                "description": "Умеренное снижение"
            }
        }
        
        stress_results = {}
        for scenario_name, scenario in scenarios.items():
            # Применение шока к данным
            stressed_returns = returns + scenario["shock"]
            stressed_var = np.percentile(stressed_returns, 5)  # 95% VaR
            
            stress_results[scenario_name] = {
                "shock": scenario["shock"],
                "description": scenario["description"],
                "stressed_var": float(stressed_var),
                "impact": float(stressed_var - np.percentile(returns, 5))
            }
            
        return {
            "scenarios": stress_results,
            "worst_case": min(
                stress_results.values(),
                key=lambda x: x["stressed_var"]
            )
        }
        
    async def _analyze_volatility(
        self, 
        market_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Анализ волатильности
        
        Args:
            market_data: Рыночные данные
            
        Returns:
            Анализ волатильности
        """
        returns = market_data['returns'].values
        
        # Простая волатильность
        volatility = np.std(returns) * np.sqrt(252)  # Годовая волатильность
        
        # Rolling volatility (30 дней)
        rolling_vol = market_data['returns'].rolling(window=30).std() * np.sqrt(252)
        current_vol = rolling_vol.iloc[-1] if not rolling_vol.empty else volatility
        
        # GARCH модель (упрощенная)
        # TODO: Реализовать полную GARCH модель
        
        return {
            "annual_volatility": float(volatility),
            "current_30d_volatility": float(current_vol) if not pd.isna(current_vol) else float(volatility),
            "volatility_trend": "increasing" if current_vol > volatility else "decreasing",
            "volatility_percentile": float(np.percentile(rolling_vol.dropna(), 50)) if not rolling_vol.empty else float(volatility)
        }
        
    async def _analyze_correlations(
        self, 
        market_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Анализ корреляций
        
        Args:
            market_data: Рыночные данные
            
        Returns:
            Анализ корреляций
        """
        # TODO: Реализовать анализ корреляций между активами
        # Пока что возвращаем базовую информацию
        
        returns = market_data['returns'].values
        
        # Автокорреляция (lag 1)
        if len(returns) > 1:
            autocorr = np.corrcoef(returns[:-1], returns[1:])[0, 1]
        else:
            autocorr = 0.0
            
        return {
            "autocorrelation_lag1": float(autocorr),
            "note": "Full correlation matrix analysis will be implemented with multi-asset data"
        }
        
    async def _generate_recommendations(
        self,
        var_results: Dict[str, Any],
        stress_results: Dict[str, Any],
        volatility_analysis: Dict[str, Any],
        correlation_analysis: Dict[str, Any]
    ) -> list:
        """
        Генерация рекомендаций на основе анализа
        
        Args:
            var_results: Результаты VaR/CVaR
            stress_results: Результаты стресс-теста
            volatility_analysis: Анализ волатильности
            correlation_analysis: Анализ корреляций
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Анализ VaR
        var_value = abs(var_results.get("var_historical", 0))
        if var_value > 0.05:  # >5%
            recommendations.append({
                "type": "warning",
                "message": f"Высокий VaR ({var_value:.2%}). Рекомендуется снизить риск.",
                "priority": "high"
            })
            
        # Анализ стресс-теста
        worst_case = stress_results.get("worst_case", {})
        if worst_case.get("impact", 0) < -0.15:  # >15% потери
            recommendations.append({
                "type": "alert",
                "message": f"Критический сценарий: {worst_case.get('description')}. Потери могут составить {worst_case.get('impact', 0):.2%}",
                "priority": "critical"
            })
            
        # Анализ волатильности
        if volatility_analysis.get("volatility_trend") == "increasing":
            recommendations.append({
                "type": "info",
                "message": "Волатильность растет. Рекомендуется усилить мониторинг.",
                "priority": "medium"
            })
            
        return recommendations
        
    def _calculate_overall_risk_score(
        self,
        var_results: Dict[str, Any],
        stress_results: Dict[str, Any],
        volatility_analysis: Dict[str, Any]
    ) -> float:
        """
        Расчет общего скора риска (0-100)
        
        Args:
            var_results: Результаты VaR/CVaR
            stress_results: Результаты стресс-теста
            volatility_analysis: Анализ волатильности
            
        Returns:
            Общий скор риска (0-100, где 100 - максимальный риск)
        """
        # Нормализация компонентов
        var_score = min(abs(var_results.get("var_historical", 0)) * 100, 50)
        stress_score = min(abs(stress_results.get("worst_case", {}).get("impact", 0)) * 100, 30)
        vol_score = min(volatility_analysis.get("annual_volatility", 0) * 100, 20)
        
        overall_score = var_score + stress_score + vol_score
        
        return min(overall_score, 100.0)
        
    async def _report_result(self, result: Dict[str, Any]):
        """
        Отчет о результатах анализа
        
        Args:
            result: Результаты анализа
        """
        # TODO: Сохранение результатов в БД
        # TODO: Отправка алертов при необходимости
        
        # Обновление графа зависимостей
        try:
            from backend.main import graph_builder_instance
            if graph_builder_instance:
                await graph_builder_instance.update_graph_from_risk_analysis(result)
        except Exception as e:
            logger.warning(f"Failed to update graph: {e}")
        
        logger.info(
            f"Market Risk Agent completed analysis for {result.get('entity_id')}. "
            f"Risk score: {result.get('risk_score', 0):.2f}"
        )
        
        # Генерация алертов при высоком риске
        if result.get("risk_score", 0) > 70:
            logger.warning(
                f"High market risk detected for {result.get('entity_id')}: "
                f"{result.get('risk_score', 0):.2f}"
            )

