"""
ARIN Platform - Regulatory Risk Agent
Агент для анализа регуляторного риска
"""
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

from backend.agents.base_agent import BaseAgent, AgentStatus
from backend.config import settings

logger = logging.getLogger(__name__)


class RegulatoryRiskAgent(BaseAgent):
    """Агент для анализа регуляторного риска"""
    
    def __init__(self, agent_id: str = "regulatory_risk_agent", config: Optional[Dict[str, Any]] = None):
        """
        Инициализация Regulatory Risk Agent
        
        Args:
            agent_id: ID агента
            config: Конфигурация агента
        """
        if config is None:
            config = {}
            
        super().__init__(
            agent_id=agent_id,
            agent_name="Regulatory Risk Agent",
            config=config
        )
        
        self.db_engine = None
        self.regulatory_db_client = None
        self.llm_client = None
        
    async def _setup_data_access(self):
        """Настройка доступа к данным"""
        try:
            # TODO: Настроить подключение к БД
            # from sqlalchemy import create_engine
            # self.db_engine = create_engine(settings.database_url)
            
            # Опциональная интеграция с регуляторными базами данных
            if self.config.get("regulatory_db_url"):
                # TODO: Интеграция с регуляторными базами (SEC EDGAR, FINRA, FCA и т.д.)
                logger.info("Regulatory database integration available")
            else:
                logger.info("Regulatory database integration not configured (optional)")
                
            logger.info("Regulatory Risk Agent data access setup completed")
        except Exception as e:
            logger.error(f"Failed to setup data access: {e}")
            raise
            
    async def _setup_ai_integration(self):
        """Настройка AI интеграции"""
        try:
            # Приоритет: DeepSeek R1 через NVIDIA API для reasoning
            if self.config.get("nvidia_api_key"):
                try:
                    from openai import OpenAI
                    self.llm_client = OpenAI(
                        base_url="https://integrate.api.nvidia.com/v1",
                        api_key=self.config.get("nvidia_api_key")
                    )
                    logger.info("DeepSeek R1 (NVIDIA API) client initialized for regulatory analysis")
                except Exception as e:
                    logger.warning(f"Failed to initialize DeepSeek R1 client: {e}")
                    self.llm_client = None
            else:
                self.llm_client = None
                logger.info("NVIDIA API key not configured")
                    
            # GPT-4 как fallback
            if self.config.get("openai_api_key"):
                try:
                    from openai import OpenAI
                    self.llm_client = OpenAI(api_key=self.config.get("openai_api_key"))
                    logger.info("OpenAI (GPT-4) client initialized (fallback)")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI client: {e}")
                    self.llm_client = None
            else:
                if not self.llm_client:
                    logger.info("OpenAI API key not configured")
            
            logger.info("Regulatory Risk Agent AI integration setup completed")
        except Exception as e:
            logger.error(f"Failed to setup AI integration: {e}")
            raise
            
    async def analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ регуляторного риска
        
        Args:
            task: Задача для анализа
                - entity_id: ID сущности (компания, портфель)
                - entity_type: Тип сущности
                - parameters: Дополнительные параметры
                
        Returns:
            Результаты анализа регуляторного риска
        """
        entity_id = task.get("entity_id")
        entity_type = task.get("entity_type", "company")
        parameters = task.get("parameters", {})
        
        logger.info(f"Analyzing regulatory risk for {entity_type} {entity_id}")
        
        try:
            # 1. Мониторинг изменений в регуляциях
            regulatory_changes = await self._monitor_regulatory_changes(entity_id, parameters)
            
            # 2. Анализ соответствия требованиям
            compliance_analysis = await self._analyze_compliance(entity_id, entity_type, parameters)
            
            # 3. Предсказание регуляторных изменений
            regulatory_predictions = await self._predict_regulatory_changes(regulatory_changes)
            
            # 4. Анализ регуляторных рисков по юрисдикциям
            jurisdiction_analysis = await self._analyze_jurisdictions(entity_id, parameters)
            
            # 5. LLM анализ для качественной оценки
            llm_analysis = await self._llm_regulatory_analysis(
                entity_id, compliance_analysis, regulatory_changes, regulatory_predictions
            )
            
            # 6. Генерация рекомендаций
            recommendations = await self._generate_recommendations(
                compliance_analysis, regulatory_changes, regulatory_predictions, jurisdiction_analysis
            )
            
            result = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "timestamp": datetime.now().isoformat(),
                "regulatory_changes": regulatory_changes,
                "compliance_analysis": compliance_analysis,
                "regulatory_predictions": regulatory_predictions,
                "jurisdiction_analysis": jurisdiction_analysis,
                "llm_analysis": llm_analysis,
                "recommendations": recommendations,
                "risk_score": self._calculate_overall_risk_score(
                    compliance_analysis, regulatory_changes, regulatory_predictions
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze regulatory risk: {e}")
            raise
            
    async def _monitor_regulatory_changes(
        self, 
        entity_id: Optional[str], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Мониторинг изменений в регуляциях
        
        Args:
            entity_id: ID сущности
            parameters: Параметры мониторинга
            
        Returns:
            Информация об изменениях в регуляциях
        """
        # TODO: Интеграция с регуляторными базами данных
        # Пока что возвращаем примерные данные
        
        # Примерные данные об изменениях
        recent_changes = [
            {
                "date": (datetime.now() - timedelta(days=5)).isoformat(),
                "jurisdiction": "US",
                "regulator": "SEC",
                "change_type": "new_rule",
                "title": "Enhanced Disclosure Requirements",
                "impact": "medium",
                "effective_date": (datetime.now() + timedelta(days=90)).isoformat()
            },
            {
                "date": (datetime.now() - timedelta(days=15)).isoformat(),
                "jurisdiction": "EU",
                "regulator": "ESMA",
                "change_type": "amendment",
                "title": "MiFID II Updates",
                "impact": "high",
                "effective_date": (datetime.now() + timedelta(days=180)).isoformat()
            }
        ]
        
        return {
            "recent_changes": recent_changes,
            "total_changes_30d": len(recent_changes),
            "high_impact_changes": sum(1 for c in recent_changes if c["impact"] == "high"),
            "medium_impact_changes": sum(1 for c in recent_changes if c["impact"] == "medium"),
            "low_impact_changes": sum(1 for c in recent_changes if c["impact"] == "low"),
            "jurisdictions_affected": list(set(c["jurisdiction"] for c in recent_changes))
        }
        
    async def _analyze_compliance(
        self, 
        entity_id: Optional[str], 
        entity_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ соответствия требованиям
        
        Args:
            entity_id: ID сущности
            entity_type: Тип сущности
            parameters: Параметры анализа
            
        Returns:
            Результаты анализа соответствия
        """
        # TODO: Интеграция с системами compliance
        # Пока что возвращаем примерные данные
        
        # Примерные требования по юрисдикциям
        compliance_requirements = {
            "US": {
                "sec_compliance": 0.92,
                "finra_compliance": 0.88,
                "cftc_compliance": 0.95,
                "overall_score": 0.92
            },
            "EU": {
                "mifid_ii_compliance": 0.90,
                "gdpr_compliance": 0.85,
                "overall_score": 0.88
            },
            "UK": {
                "fca_compliance": 0.91,
                "pca_compliance": 0.89,
                "overall_score": 0.90
            }
        }
        
        # Выявление несоответствий
        non_compliances = []
        for jurisdiction, scores in compliance_requirements.items():
            overall = scores.get("overall_score", 1.0)
            if overall < 0.9:
                non_compliances.append({
                    "jurisdiction": jurisdiction,
                    "compliance_score": overall,
                    "severity": "high" if overall < 0.85 else "medium",
                    "description": f"Низкий уровень соответствия в {jurisdiction}"
                })
        
        return {
            "compliance_scores": compliance_requirements,
            "overall_compliance_score": np.mean([
                scores.get("overall_score", 1.0) 
                for scores in compliance_requirements.values()
            ]),
            "non_compliances": non_compliances,
            "compliance_trend": "stable",  # TODO: Рассчитать тренд
            "next_audit_date": (datetime.now() + timedelta(days=90)).isoformat()
        }
        
    async def _predict_regulatory_changes(
        self, 
        regulatory_changes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Предсказание регуляторных изменений
        
        Args:
            regulatory_changes: Данные об изменениях в регуляциях
            
        Returns:
            Предсказания регуляторных изменений
        """
        # Простая модель предсказания на основе исторических данных
        # В production это будет более сложная модель с LLM
        
        recent_changes = regulatory_changes.get("recent_changes", [])
        
        # Анализ трендов
        high_impact_count = regulatory_changes.get("high_impact_changes", 0)
        
        # Вероятность новых изменений в ближайшие 90 дней
        if high_impact_count > 0:
            prediction_probability = 0.7
        else:
            prediction_probability = 0.4
        
        # Ожидаемые области изменений
        expected_areas = []
        if high_impact_count > 0:
            expected_areas = [
                "Enhanced disclosure requirements",
                "Risk management standards",
                "Capital adequacy requirements"
            ]
        
        return {
            "probability_new_changes_90d": prediction_probability,
            "expected_impact": "medium" if prediction_probability > 0.5 else "low",
            "expected_areas": expected_areas,
            "confidence": 0.65,
            "recommended_actions": [
                "Мониторинг регуляторных обновлений",
                "Подготовка к потенциальным изменениям",
                "Обновление compliance процедур"
            ] if prediction_probability > 0.5 else []
        }
        
    async def _analyze_jurisdictions(
        self, 
        entity_id: Optional[str], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ регуляторных рисков по юрисдикциям
        
        Args:
            entity_id: ID сущности
            parameters: Параметры анализа
            
        Returns:
            Анализ по юрисдикциям
        """
        jurisdictions = ["US", "EU", "UK", "APAC"]
        
        jurisdiction_risks = {}
        for jurisdiction in jurisdictions:
            # Упрощенная оценка риска по юрисдикции
            base_risk = np.random.uniform(0.1, 0.4)
            
            jurisdiction_risks[jurisdiction] = {
                "regulatory_risk_score": float(base_risk),
                "risk_level": "high" if base_risk > 0.3 else "medium" if base_risk > 0.2 else "low",
                "key_regulators": self._get_regulators_for_jurisdiction(jurisdiction),
                "recent_activity": "high" if base_risk > 0.3 else "medium"
            }
        
        return {
            "jurisdictions": jurisdiction_risks,
            "highest_risk_jurisdiction": max(
                jurisdiction_risks.items(),
                key=lambda x: x[1]["regulatory_risk_score"]
            )[0],
            "average_risk_score": float(np.mean([
                j["regulatory_risk_score"] 
                for j in jurisdiction_risks.values()
            ]))
        }
        
    def _get_regulators_for_jurisdiction(self, jurisdiction: str) -> List[str]:
        """Получение списка регуляторов для юрисдикции"""
        regulators_map = {
            "US": ["SEC", "FINRA", "CFTC", "OCC", "FDIC"],
            "EU": ["ESMA", "ECB", "EBA"],
            "UK": ["FCA", "PRA", "Bank of England"],
            "APAC": ["ASIC", "HKMA", "MAS", "JFSA"]
        }
        return regulators_map.get(jurisdiction, [])
        
    async def _llm_regulatory_analysis(
        self,
        entity_id: Optional[str],
        compliance_analysis: Dict[str, Any],
        regulatory_changes: Dict[str, Any],
        regulatory_predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        LLM анализ регуляторного риска
        
        Args:
            entity_id: ID сущности
            compliance_analysis: Анализ соответствия
            regulatory_changes: Изменения в регуляциях
            regulatory_predictions: Предсказания изменений
            
        Returns:
            Результаты LLM анализа
        """
        if not self.llm_client:
            return {
                "analysis": "LLM analysis not available (no API keys configured)",
                "model": None
            }
            
        try:
            context = f"""
Регуляторный анализ для {entity_id}:

Соответствие требованиям:
- Общий показатель соответствия: {compliance_analysis.get('overall_compliance_score', 0):.2%}
- Несоответствия: {len(compliance_analysis.get('non_compliances', []))}

Изменения в регуляциях:
- Изменений за 30 дней: {regulatory_changes.get('total_changes_30d', 0)}
- Высокое влияние: {regulatory_changes.get('high_impact_changes', 0)}

Предсказания:
- Вероятность новых изменений (90 дней): {regulatory_predictions.get('probability_new_changes_90d', 0):.1%}
"""
            
            prompt = f"""
Проанализируй регуляторные риски на основе следующих данных:

{context}

Предоставь:
1. Качественную оценку регуляторного риска
2. Основные проблемные области соответствия
3. Потенциальные последствия регуляторных изменений
4. Приоритетные рекомендации по улучшению соответствия

Ответ должен быть структурированным и конкретным.
"""
            
            # Приоритет: DeepSeek R1 через NVIDIA API
            if hasattr(self.llm_client, 'base_url') and 'nvidia.com' in str(self.llm_client.base_url):
                try:
                    completion = self.llm_client.chat.completions.create(
                        model="deepseek-ai/deepseek-r1",
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.6,
                        top_p=0.7,
                        max_tokens=2048,
                        stream=False
                    )
                    
                    reasoning_content = getattr(completion.choices[0].message, "reasoning_content", None)
                    content = completion.choices[0].message.content
                    
                    return {
                        "analysis": content,
                        "reasoning": reasoning_content,
                        "model": "deepseek-r1-nvidia"
                    }
                except Exception as e:
                    logger.warning(f"DeepSeek R1 analysis failed: {e}, trying fallback")
            
            # Fallback: GPT-4
            completion = self.llm_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=2048
            )
            
            return {
                "analysis": completion.choices[0].message.content,
                "model": "gpt-4"
            }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "analysis": f"LLM analysis failed: {str(e)}",
                "model": None
            }
            
    async def _generate_recommendations(
        self,
        compliance_analysis: Dict[str, Any],
        regulatory_changes: Dict[str, Any],
        regulatory_predictions: Dict[str, Any],
        jurisdiction_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Генерация рекомендаций
        
        Args:
            compliance_analysis: Анализ соответствия
            regulatory_changes: Изменения в регуляциях
            regulatory_predictions: Предсказания изменений
            jurisdiction_analysis: Анализ по юрисдикциям
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Рекомендации по соответствию
        overall_compliance = compliance_analysis.get("overall_compliance_score", 1.0)
        if overall_compliance < 0.9:
            recommendations.append({
                "priority": "high",
                "category": "compliance",
                "title": "Улучшение соответствия регуляторным требованиям",
                "description": f"Общий показатель соответствия {overall_compliance:.2%} ниже целевого уровня. Рекомендуется провести аудит соответствия.",
                "impact": "Снижение регуляторных рисков и потенциальных штрафов"
            })
        
        # Рекомендации по несоответствиям
        for non_compliance in compliance_analysis.get("non_compliances", []):
            if non_compliance["severity"] == "high":
                recommendations.append({
                    "priority": "high",
                    "category": "non_compliance",
                    "title": f"Критическое несоответствие в {non_compliance['jurisdiction']}",
                    "description": non_compliance["description"],
                    "impact": "Риск регуляторных санкций"
                })
        
        # Рекомендации по изменениям в регуляциях
        high_impact_changes = regulatory_changes.get("high_impact_changes", 0)
        if high_impact_changes > 0:
            recommendations.append({
                "priority": "high",
                "category": "regulatory_changes",
                "title": "Активные изменения в регуляциях требуют внимания",
                "description": f"Обнаружено {high_impact_changes} изменений с высоким влиянием. Рекомендуется обновить процедуры соответствия.",
                "impact": "Снижение риска несоответствия новым требованиям"
            })
        
        # Рекомендации на основе предсказаний
        if regulatory_predictions.get("probability_new_changes_90d", 0) > 0.5:
            recommendations.append({
                "priority": "medium",
                "category": "preparation",
                "title": "Подготовка к ожидаемым регуляторным изменениям",
                "description": "Высокая вероятность новых регуляторных изменений. Рекомендуется начать подготовку заранее.",
                "impact": "Снижение затрат на адаптацию к новым требованиям"
            })
        
        return recommendations
        
    def _calculate_overall_risk_score(
        self,
        compliance_analysis: Dict[str, Any],
        regulatory_changes: Dict[str, Any],
        regulatory_predictions: Dict[str, Any]
    ) -> float:
        """
        Расчет общего показателя регуляторного риска
        
        Args:
            compliance_analysis: Анализ соответствия
            regulatory_changes: Изменения в регуляциях
            regulatory_predictions: Предсказания изменений
            
        Returns:
            Общий показатель риска (0-1, где 1 = максимальный риск)
        """
        # Компоненты риска
        compliance_risk = 1 - compliance_analysis.get("overall_compliance_score", 1.0)
        
        # Риск от изменений
        high_impact_changes = regulatory_changes.get("high_impact_changes", 0)
        change_risk = min(high_impact_changes * 0.15, 0.4)
        
        # Риск от предсказаний
        prediction_risk = regulatory_predictions.get("probability_new_changes_90d", 0) * 0.3
        
        # Взвешенная сумма
        overall_risk = (
            compliance_risk * 0.5 +
            change_risk * 0.3 +
            prediction_risk * 0.2
        )
        
        return float(min(overall_risk, 1.0))
        
    async def _report_result(self, result: Dict[str, Any]):
        """Отчет о результатах анализа"""
        logger.info(f"Regulatory Risk Agent completed analysis for {result.get('entity_id')}")
        # TODO: Сохранение результатов в БД или отправка в Graph Builder
        pass

