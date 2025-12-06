"""
ARIN Platform - Liquidity Risk Agent
Агент для анализа риска ликвидности
"""
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backend.agents.base_agent import BaseAgent, AgentStatus
from backend.config import settings

logger = logging.getLogger(__name__)


class LiquidityRiskAgent(BaseAgent):
    """Агент для анализа риска ликвидности"""
    
    def __init__(self, agent_id: str = "liquidity_risk_agent", config: Optional[Dict[str, Any]] = None):
        """
        Инициализация Liquidity Risk Agent
        
        Args:
            agent_id: ID агента
            config: Конфигурация агента
        """
        if config is None:
            config = {}
            
        super().__init__(
            agent_id=agent_id,
            agent_name="Liquidity Risk Agent",
            config=config
        )
        
        self.db_engine = None
        self.liquidity_positioner_client = None
        
    async def _setup_data_access(self):
        """Настройка доступа к данным"""
        try:
            # TODO: Настроить подключение к БД
            # from sqlalchemy import create_engine
            # self.db_engine = create_engine(settings.database_url)
            
            # Опциональная интеграция с Liquidity Positioner
            if self.config.get("liquidity_positioner_url"):
                # TODO: Интеграция с Liquidity Positioner Platform
                logger.info("Liquidity Positioner integration available")
            else:
                logger.info("Liquidity Positioner integration not configured (optional)")
                
            logger.info("Liquidity Risk Agent data access setup completed")
        except Exception as e:
            logger.error(f"Failed to setup data access: {e}")
            raise
            
    async def _setup_ai_integration(self):
        """Настройка AI интеграции"""
        try:
            # Для ликвидности AI используется реже, но может быть полезен для анализа сценариев
            logger.info("Liquidity Risk Agent AI integration setup completed")
        except Exception as e:
            logger.error(f"Failed to setup AI integration: {e}")
            raise
            
    async def analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ риска ликвидности
        
        Args:
            task: Задача для анализа
                - entity_id: ID сущности (портфель, баланс)
                - entity_type: Тип сущности
                - parameters: Дополнительные параметры
                
        Returns:
            Результаты анализа риска ликвидности
        """
        entity_id = task.get("entity_id")
        entity_type = task.get("entity_type", "balance_sheet")
        parameters = task.get("parameters", {})
        
        logger.info(f"Analyzing liquidity risk for {entity_type} {entity_id}")
        
        try:
            # 1. Получение данных о ликвидности
            liquidity_data = await self._get_liquidity_data(entity_id, entity_type)
            
            # 2. Расчет LCR (Liquidity Coverage Ratio)
            lcr = await self._calculate_lcr(liquidity_data, parameters)
            
            # 3. Расчет NSFR (Net Stable Funding Ratio)
            nsfr = await self._calculate_nsfr(liquidity_data, parameters)
            
            # 4. Мониторинг ликвидности
            liquidity_monitoring = await self._monitor_liquidity(liquidity_data)
            
            # 5. Стресс-тестирование ликвидности
            stress_test_results = await self._stress_test_liquidity(liquidity_data, parameters)
            
            # 6. Анализ временных горизонтов
            maturity_analysis = await self._analyze_maturity_profile(liquidity_data)
            
            # 7. Генерация рекомендаций
            recommendations = await self._generate_recommendations(
                lcr, nsfr, liquidity_monitoring, stress_test_results
            )
            
            result = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "timestamp": datetime.now().isoformat(),
                "lcr": lcr,
                "nsfr": nsfr,
                "liquidity_monitoring": liquidity_monitoring,
                "stress_test_results": stress_test_results,
                "maturity_analysis": maturity_analysis,
                "recommendations": recommendations,
                "risk_score": self._calculate_overall_risk_score(
                    lcr, nsfr, liquidity_monitoring, stress_test_results
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze liquidity risk: {e}")
            raise
            
    async def _get_liquidity_data(
        self, 
        entity_id: Optional[str], 
        entity_type: str
    ) -> pd.DataFrame:
        """
        Получение данных о ликвидности
        
        Args:
            entity_id: ID сущности
            entity_type: Тип сущности
            
        Returns:
            DataFrame с данными о ликвидности
        """
        # TODO: Реализовать получение данных из БД или внешних источников
        # Пока что возвращаем примерные данные для тестирования
        
        # Генерация тестовых данных о ликвидности
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        
        np.random.seed(42)
        
        # HQLA (High Quality Liquid Assets)
        hqla = 100000000 + np.random.normal(0, 5000000, len(dates))
        
        # Cash outflows (оттоки)
        cash_outflows_30d = np.random.normal(50000000, 5000000, len(dates))
        cash_outflows_90d = cash_outflows_30d * 2.5 + np.random.normal(0, 2000000, len(dates))
        
        # Cash inflows (притоки)
        cash_inflows_30d = np.random.normal(45000000, 4000000, len(dates))
        cash_inflows_90d = cash_inflows_30d * 2.3 + np.random.normal(0, 2000000, len(dates))
        
        # Net cash flows
        net_cash_flow_30d = cash_inflows_30d - cash_outflows_30d
        net_cash_flow_90d = cash_inflows_90d - cash_outflows_90d
        
        # Available Stable Funding (ASF)
        asf = 200000000 + np.random.normal(0, 10000000, len(dates))
        
        # Required Stable Funding (RSF)
        rsf = 150000000 + np.random.normal(0, 8000000, len(dates))
        
        data = pd.DataFrame({
            'date': dates,
            'hqla': hqla,
            'cash_outflows_30d': cash_outflows_30d,
            'cash_outflows_90d': cash_outflows_90d,
            'cash_inflows_30d': cash_inflows_30d,
            'cash_inflows_90d': cash_inflows_90d,
            'net_cash_flow_30d': net_cash_flow_30d,
            'net_cash_flow_90d': net_cash_flow_90d,
            'asf': asf,
            'rsf': rsf,
            'total_assets': 500000000 + np.random.normal(0, 20000000, len(dates))
        })
        
        return data
        
    async def _calculate_lcr(
        self, 
        liquidity_data: pd.DataFrame, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Расчет LCR (Liquidity Coverage Ratio)
        
        LCR = HQLA / Net Cash Outflows (30 days)
        
        Args:
            liquidity_data: Данные о ликвидности
            parameters: Параметры расчета
            
        Returns:
            Результаты расчета LCR
        """
        latest = liquidity_data.iloc[-1]
        
        hqla = latest['hqla']
        net_cash_outflows_30d = max(
            latest['cash_outflows_30d'] - latest['cash_inflows_30d'],
            0
        )
        
        # LCR расчет
        if net_cash_outflows_30d > 0:
            lcr_ratio = hqla / net_cash_outflows_30d
        else:
            lcr_ratio = float('inf')  # Нет оттоков - идеальная ликвидность
        
        # Регуляторное требование: LCR >= 100%
        regulatory_requirement = 1.0
        compliance = lcr_ratio >= regulatory_requirement
        
        # Оценка риска
        if lcr_ratio >= 1.2:
            risk_level = "low"
        elif lcr_ratio >= 1.0:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "lcr_ratio": float(lcr_ratio) if lcr_ratio != float('inf') else 999.0,
            "hqla": float(hqla),
            "net_cash_outflows_30d": float(net_cash_outflows_30d),
            "regulatory_requirement": regulatory_requirement,
            "compliance": compliance,
            "risk_level": risk_level,
            "buffer": float(lcr_ratio - regulatory_requirement) if lcr_ratio != float('inf') else 999.0
        }
        
    async def _calculate_nsfr(
        self, 
        liquidity_data: pd.DataFrame, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Расчет NSFR (Net Stable Funding Ratio)
        
        NSFR = Available Stable Funding (ASF) / Required Stable Funding (RSF)
        
        Args:
            liquidity_data: Данные о ликвидности
            parameters: Параметры расчета
            
        Returns:
            Результаты расчета NSFR
        """
        latest = liquidity_data.iloc[-1]
        
        asf = latest['asf']
        rsf = latest['rsf']
        
        # NSFR расчет
        if rsf > 0:
            nsfr_ratio = asf / rsf
        else:
            nsfr_ratio = float('inf')
        
        # Регуляторное требование: NSFR >= 100%
        regulatory_requirement = 1.0
        compliance = nsfr_ratio >= regulatory_requirement
        
        # Оценка риска
        if nsfr_ratio >= 1.1:
            risk_level = "low"
        elif nsfr_ratio >= 1.0:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "nsfr_ratio": float(nsfr_ratio) if nsfr_ratio != float('inf') else 999.0,
            "asf": float(asf),
            "rsf": float(rsf),
            "regulatory_requirement": regulatory_requirement,
            "compliance": compliance,
            "risk_level": risk_level,
            "buffer": float(nsfr_ratio - regulatory_requirement) if nsfr_ratio != float('inf') else 999.0
        }
        
    async def _monitor_liquidity(
        self, 
        liquidity_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Мониторинг ликвидности
        
        Args:
            liquidity_data: Данные о ликвидности
            
        Returns:
            Результаты мониторинга
        """
        latest = liquidity_data.iloc[-1]
        recent_data = liquidity_data.tail(30)
        
        # Тренды
        hqla_trend = recent_data['hqla'].diff().mean()
        net_cash_flow_trend = recent_data['net_cash_flow_30d'].diff().mean()
        
        # Волатильность
        hqla_volatility = recent_data['hqla'].std() / recent_data['hqla'].mean()
        cash_flow_volatility = recent_data['net_cash_flow_30d'].std()
        
        # Анализ ликвидных позиций
        min_hqla = recent_data['hqla'].min()
        max_hqla = recent_data['hqla'].max()
        avg_hqla = recent_data['hqla'].mean()
        
        return {
            "current_hqla": float(latest['hqla']),
            "average_hqla_30d": float(avg_hqla),
            "min_hqla_30d": float(min_hqla),
            "max_hqla_30d": float(max_hqla),
            "hqla_trend": "increasing" if hqla_trend > 0 else "decreasing",
            "net_cash_flow_trend": "positive" if net_cash_flow_trend > 0 else "negative",
            "hqla_volatility": float(hqla_volatility),
            "cash_flow_volatility": float(cash_flow_volatility),
            "liquidity_health": "good" if latest['hqla'] > avg_hqla * 0.9 else "warning"
        }
        
    async def _stress_test_liquidity(
        self, 
        liquidity_data: pd.DataFrame, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Стресс-тестирование ликвидности
        
        Args:
            liquidity_data: Данные о ликвидности
            parameters: Параметры стресс-теста
            
        Returns:
            Результаты стресс-тестирования
        """
        latest = liquidity_data.iloc[-1]
        
        # Сценарии стресс-теста
        scenarios = {
            "mild_stress": {
                "hqla_shock": -0.10,  # -10% HQLA
                "outflow_shock": 0.20,  # +20% оттоков
                "description": "Умеренный стресс"
            },
            "moderate_stress": {
                "hqla_shock": -0.20,  # -20% HQLA
                "outflow_shock": 0.40,  # +40% оттоков
                "description": "Умеренный стресс"
            },
            "severe_stress": {
                "hqla_shock": -0.30,  # -30% HQLA
                "outflow_shock": 0.60,  # +60% оттоков
                "description": "Суровый стресс"
            }
        }
        
        stress_results = {}
        base_hqla = latest['hqla']
        base_outflows = latest['cash_outflows_30d']
        base_inflows = latest['cash_inflows_30d']
        
        for scenario_name, scenario in scenarios.items():
            # Применение шоков
            stressed_hqla = base_hqla * (1 + scenario["hqla_shock"])
            stressed_outflows = base_outflows * (1 + scenario["outflow_shock"])
            stressed_net_outflows = max(stressed_outflows - base_inflows, 0)
            
            # Расчет LCR в стресс-сценарии
            if stressed_net_outflows > 0:
                stressed_lcr = stressed_hqla / stressed_net_outflows
            else:
                stressed_lcr = float('inf')
            
            stress_results[scenario_name] = {
                "description": scenario["description"],
                "stressed_lcr": float(stressed_lcr) if stressed_lcr != float('inf') else 999.0,
                "stressed_hqla": float(stressed_hqla),
                "stressed_net_outflows": float(stressed_net_outflows),
                "lcr_deterioration": float(stressed_lcr - (base_hqla / max(base_outflows - base_inflows, 1))) if stressed_lcr != float('inf') else 0,
                "survival_days": float(stressed_hqla / max(stressed_net_outflows / 30, 1)) if stressed_net_outflows > 0 else 999.0
            }
        
        return {
            "scenarios": stress_results,
            "worst_case": min(
                stress_results.values(),
                key=lambda x: x["stressed_lcr"]
            )
        }
        
    async def _analyze_maturity_profile(
        self, 
        liquidity_data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Анализ профиля погашения
        
        Args:
            liquidity_data: Данные о ликвидности
            
        Returns:
            Анализ профиля погашения
        """
        latest = liquidity_data.iloc[-1]
        
        # Упрощенный анализ (в реальности нужны детальные данные по срокам)
        return {
            "short_term_liabilities_30d": float(latest.get('cash_outflows_30d', 0)),
            "short_term_assets_30d": float(latest.get('cash_inflows_30d', 0)),
            "maturity_gap_30d": float(latest.get('net_cash_flow_30d', 0)),
            "concentration_risk": "low",  # TODO: Реализовать расчет концентрации
            "note": "Detailed maturity profile analysis requires additional data"
        }
        
    async def _generate_recommendations(
        self,
        lcr: Dict[str, Any],
        nsfr: Dict[str, Any],
        liquidity_monitoring: Dict[str, Any],
        stress_test_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Генерация рекомендаций
        
        Args:
            lcr: Результаты LCR
            nsfr: Результаты NSFR
            liquidity_monitoring: Мониторинг ликвидности
            stress_test_results: Результаты стресс-теста
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Рекомендации по LCR
        if lcr.get("risk_level") == "high":
            recommendations.append({
                "priority": "high",
                "category": "lcr",
                "title": "Критический LCR - требуется немедленное действие",
                "description": f"LCR составляет {lcr['lcr_ratio']:.2%}, что ниже регуляторного требования. Необходимо увеличить HQLA или снизить оттоки.",
                "impact": "Риск несоответствия регуляторным требованиям"
            })
        elif lcr.get("risk_level") == "medium":
            recommendations.append({
                "priority": "medium",
                "category": "lcr",
                "title": "LCR на границе требований",
                "description": f"LCR составляет {lcr['lcr_ratio']:.2%}. Рекомендуется создать буфер выше минимального требования.",
                "impact": "Повышение устойчивости к стрессам"
            })
        
        # Рекомендации по NSFR
        if nsfr.get("risk_level") == "high":
            recommendations.append({
                "priority": "high",
                "category": "nsfr",
                "title": "Критический NSFR - требуется действие",
                "description": f"NSFR составляет {nsfr['nsfr_ratio']:.2%}, что ниже регуляторного требования. Необходимо увеличить ASF или снизить RSF.",
                "impact": "Риск несоответствия регуляторным требованиям"
            })
        
        # Рекомендации по стресс-тесту
        worst_case = stress_test_results.get("worst_case", {})
        if worst_case.get("stressed_lcr", 1) < 1.0:
            recommendations.append({
                "priority": "high",
                "category": "stress_test",
                "title": "Уязвимость в стресс-сценариях",
                "description": f"В суровом стресс-сценарии LCR падает до {worst_case.get('stressed_lcr', 0):.2%}. Рекомендуется увеличить буфер ликвидности.",
                "impact": f"Выживаемость: {worst_case.get('survival_days', 0):.1f} дней"
            })
        
        # Рекомендации по мониторингу
        if liquidity_monitoring.get("liquidity_health") == "warning":
            recommendations.append({
                "priority": "medium",
                "category": "monitoring",
                "title": "Ухудшение ликвидности",
                "description": "Текущий уровень HQLA ниже среднего за 30 дней. Рекомендуется усилить мониторинг.",
                "impact": "Раннее выявление проблем"
            })
        
        return recommendations
        
    def _calculate_overall_risk_score(
        self,
        lcr: Dict[str, Any],
        nsfr: Dict[str, Any],
        liquidity_monitoring: Dict[str, Any],
        stress_test_results: Dict[str, Any]
    ) -> float:
        """
        Расчет общего показателя риска ликвидности
        
        Args:
            lcr: Результаты LCR
            nsfr: Результаты NSFR
            liquidity_monitoring: Мониторинг ликвидности
            stress_test_results: Результаты стресс-теста
            
        Returns:
            Общий показатель риска (0-1, где 1 = максимальный риск)
        """
        # Компоненты риска
        lcr_risk = 0.0
        if lcr.get("risk_level") == "high":
            lcr_risk = 0.5
        elif lcr.get("risk_level") == "medium":
            lcr_risk = 0.25
        else:
            lcr_risk = max(0, 0.1 - (lcr.get("lcr_ratio", 1) - 1.0) * 0.1)
        
        nsfr_risk = 0.0
        if nsfr.get("risk_level") == "high":
            nsfr_risk = 0.3
        elif nsfr.get("risk_level") == "medium":
            nsfr_risk = 0.15
        else:
            nsfr_risk = max(0, 0.05 - (nsfr.get("nsfr_ratio", 1) - 1.0) * 0.05)
        
        # Риск от стресс-теста
        worst_case = stress_test_results.get("worst_case", {})
        stress_risk = 0.0
        if worst_case.get("stressed_lcr", 1) < 1.0:
            stress_risk = 0.2
        elif worst_case.get("stressed_lcr", 1) < 1.1:
            stress_risk = 0.1
        
        # Взвешенная сумма
        overall_risk = (
            lcr_risk * 0.4 +
            nsfr_risk * 0.3 +
            stress_risk * 0.3
        )
        
        return float(min(overall_risk, 1.0))
        
    async def _report_result(self, result: Dict[str, Any]):
        """Отчет о результатах анализа"""
        logger.info(f"Liquidity Risk Agent completed analysis for {result.get('entity_id')}")
        # TODO: Сохранение результатов в БД или отправка в Graph Builder
        pass

