"""
ARIN Platform - Operational Risk Agent
Агент для анализа операционного риска
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


class OperationalRiskAgent(BaseAgent):
    """Агент для анализа операционного риска"""
    
    def __init__(self, agent_id: str = "operational_risk_agent", config: Optional[Dict[str, Any]] = None):
        """
        Инициализация Operational Risk Agent
        
        Args:
            agent_id: ID агента
            config: Конфигурация агента
        """
        if config is None:
            config = {}
            
        super().__init__(
            agent_id=agent_id,
            agent_name="Operational Risk Agent",
            config=config
        )
        
        self.db_engine = None
        self.log_analyzer = None
        self.llm_client = None
        
    async def _setup_data_access(self):
        """Настройка доступа к данным"""
        try:
            # TODO: Настроить подключение к БД
            # from sqlalchemy import create_engine
            # self.db_engine = create_engine(settings.database_url)
            
            # Настройка анализа логов (опционально)
            if self.config.get("log_analyzer_enabled", False):
                # TODO: Интеграция с системами логирования (ELK, Splunk и т.д.)
                logger.info("Log analyzer integration available")
            else:
                logger.info("Log analyzer not configured (optional)")
                
            logger.info("Operational Risk Agent data access setup completed")
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
                    logger.info("DeepSeek R1 (NVIDIA API) client initialized for operational risk analysis")
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
            
            logger.info("Operational Risk Agent AI integration setup completed")
        except Exception as e:
            logger.error(f"Failed to setup AI integration: {e}")
            raise
            
    async def analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ операционного риска
        
        Args:
            task: Задача для анализа
                - entity_id: ID сущности (процесс, система, подразделение)
                - entity_type: Тип сущности
                - parameters: Дополнительные параметры
                
        Returns:
            Результаты анализа операционного риска
        """
        entity_id = task.get("entity_id")
        entity_type = task.get("entity_type", "process")
        parameters = task.get("parameters", {})
        
        logger.info(f"Analyzing operational risk for {entity_type} {entity_id}")
        
        try:
            # 1. Получение данных о процессах
            process_data = await self._get_process_data(entity_id, entity_type)
            
            # 2. Анализ уязвимостей
            vulnerabilities = await self._identify_vulnerabilities(process_data, parameters)
            
            # 3. Анализ логов (если доступно)
            log_analysis = await self._analyze_logs(entity_id)
            
            # 4. Предсказание операционных сбоев
            failure_prediction = await self._predict_failures(process_data, log_analysis)
            
            # 5. Расчет операционных метрик
            operational_metrics = await self._calculate_operational_metrics(
                process_data, vulnerabilities, log_analysis
            )
            
            # 6. LLM анализ для качественной оценки
            llm_analysis = await self._llm_operational_analysis(
                entity_id, process_data, vulnerabilities, log_analysis
            )
            
            # 7. Генерация рекомендаций
            recommendations = await self._generate_recommendations(
                vulnerabilities, failure_prediction, operational_metrics, llm_analysis
            )
            
            result = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "timestamp": datetime.now().isoformat(),
                "vulnerabilities": vulnerabilities,
                "log_analysis": log_analysis,
                "failure_prediction": failure_prediction,
                "operational_metrics": operational_metrics,
                "llm_analysis": llm_analysis,
                "recommendations": recommendations,
                "risk_score": self._calculate_overall_risk_score(
                    vulnerabilities, failure_prediction, operational_metrics
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze operational risk: {e}")
            raise
            
    async def _get_process_data(
        self, 
        entity_id: Optional[str], 
        entity_type: str
    ) -> pd.DataFrame:
        """
        Получение данных о процессах
        
        Args:
            entity_id: ID сущности
            entity_type: Тип сущности
            
        Returns:
            DataFrame с данными о процессах
        """
        # TODO: Реализовать получение данных из БД или внешних источников
        # Пока что возвращаем примерные данные для тестирования
        
        # Генерация тестовых данных о процессах
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        
        np.random.seed(42)
        
        # Метрики процессов
        process_efficiency = 0.85 + np.random.normal(0, 0.1, len(dates))
        error_rate = np.random.exponential(0.02, len(dates))
        downtime_hours = np.random.poisson(0.5, len(dates))
        incidents_count = np.random.poisson(0.3, len(dates))
        
        data = pd.DataFrame({
            'date': dates,
            'process_efficiency': np.clip(process_efficiency, 0, 1),
            'error_rate': np.clip(error_rate, 0, 0.1),
            'downtime_hours': downtime_hours,
            'incidents_count': incidents_count,
            'manual_interventions': np.random.poisson(2, len(dates)),
            'compliance_score': 0.9 + np.random.normal(0, 0.05, len(dates))
        })
        
        return data
        
    async def _identify_vulnerabilities(
        self, 
        process_data: pd.DataFrame, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Выявление уязвимостей
        
        Args:
            process_data: Данные о процессах
            parameters: Параметры анализа
            
        Returns:
            Список выявленных уязвимостей
        """
        vulnerabilities = []
        
        latest = process_data.iloc[-1]
        recent_data = process_data.tail(30)  # Последние 30 дней
        
        # Анализ эффективности процессов
        avg_efficiency = recent_data['process_efficiency'].mean()
        if avg_efficiency < 0.7:
            vulnerabilities.append({
                "type": "low_efficiency",
                "severity": "high",
                "description": f"Низкая эффективность процессов: {avg_efficiency:.2%}",
                "impact": "Снижение производительности и увеличение операционных рисков",
                "recommendation": "Провести аудит процессов и оптимизацию"
            })
        
        # Анализ частоты ошибок
        avg_error_rate = recent_data['error_rate'].mean()
        if avg_error_rate > 0.05:
            vulnerabilities.append({
                "type": "high_error_rate",
                "severity": "high",
                "description": f"Высокая частота ошибок: {avg_error_rate:.2%}",
                "impact": "Увеличение операционных потерь и рисков",
                "recommendation": "Внедрить автоматизацию и улучшить контроль качества"
            })
        
        # Анализ простоев
        total_downtime = recent_data['downtime_hours'].sum()
        if total_downtime > 10:
            vulnerabilities.append({
                "type": "excessive_downtime",
                "severity": "medium",
                "description": f"Избыточные простои: {total_downtime:.1f} часов за 30 дней",
                "impact": "Потеря производительности и потенциальные финансовые потери",
                "recommendation": "Улучшить мониторинг и профилактическое обслуживание"
            })
        
        # Анализ инцидентов
        total_incidents = recent_data['incidents_count'].sum()
        if total_incidents > 15:
            vulnerabilities.append({
                "type": "frequent_incidents",
                "severity": "medium",
                "description": f"Частые инциденты: {total_incidents} за 30 дней",
                "impact": "Риск операционных сбоев и нарушений",
                "recommendation": "Усилить мониторинг и систему реагирования на инциденты"
            })
        
        # Анализ соответствия
        avg_compliance = recent_data['compliance_score'].mean()
        if avg_compliance < 0.85:
            vulnerabilities.append({
                "type": "compliance_risk",
                "severity": "high",
                "description": f"Риск несоответствия: {avg_compliance:.2%}",
                "impact": "Регуляторные риски и потенциальные штрафы",
                "recommendation": "Провести аудит соответствия и улучшить контроль"
            })
        
        return {
            "vulnerabilities": vulnerabilities,
            "total_count": len(vulnerabilities),
            "high_severity_count": sum(1 for v in vulnerabilities if v["severity"] == "high"),
            "medium_severity_count": sum(1 for v in vulnerabilities if v["severity"] == "medium"),
            "low_severity_count": sum(1 for v in vulnerabilities if v["severity"] == "low")
        }
        
    async def _analyze_logs(self, entity_id: Optional[str]) -> Dict[str, Any]:
        """
        Анализ логов систем
        
        Args:
            entity_id: ID сущности
            
        Returns:
            Результаты анализа логов
        """
        # TODO: Интеграция с системами логирования
        # Пока что возвращаем примерные данные
        
        return {
            "log_entries_analyzed": 0,
            "error_count": 0,
            "warning_count": 0,
            "anomalies_detected": [],
            "trends": {
                "error_trend": "stable",
                "warning_trend": "stable"
            },
            "note": "Log analysis not configured (optional integration)"
        }
        
    async def _predict_failures(
        self, 
        process_data: pd.DataFrame, 
        log_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Предсказание операционных сбоев
        
        Args:
            process_data: Данные о процессах
            log_analysis: Результаты анализа логов
            
        Returns:
            Предсказания сбоев
        """
        recent_data = process_data.tail(30)
        
        # Простая модель предсказания на основе трендов
        error_rate_trend = recent_data['error_rate'].diff().mean()
        downtime_trend = recent_data['downtime_hours'].diff().mean()
        incidents_trend = recent_data['incidents_count'].diff().mean()
        
        # Вероятность сбоя в ближайшие 7 дней
        failure_probability = 0.1  # Базовая вероятность
        
        if error_rate_trend > 0:
            failure_probability += 0.2
        if downtime_trend > 0:
            failure_probability += 0.15
        if incidents_trend > 0:
            failure_probability += 0.15
            
        failure_probability = min(failure_probability, 0.9)
        
        # Ожидаемый ущерб (упрощенная оценка)
        avg_downtime = recent_data['downtime_hours'].mean()
        expected_impact = avg_downtime * 10000  # Примерная стоимость часа простоя
        
        return {
            "failure_probability_7d": float(failure_probability),
            "failure_probability_30d": float(min(failure_probability * 1.5, 0.95)),
            "expected_impact": float(expected_impact),
            "risk_factors": {
                "error_rate_increasing": error_rate_trend > 0,
                "downtime_increasing": downtime_trend > 0,
                "incidents_increasing": incidents_trend > 0
            },
            "confidence": 0.75
        }
        
    async def _calculate_operational_metrics(
        self,
        process_data: pd.DataFrame,
        vulnerabilities: Dict[str, Any],
        log_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Расчет операционных метрик
        
        Args:
            process_data: Данные о процессах
            vulnerabilities: Выявленные уязвимости
            log_analysis: Анализ логов
            
        Returns:
            Операционные метрики
        """
        latest = process_data.iloc[-1]
        recent_data = process_data.tail(30)
        
        return {
            "process_efficiency": float(latest['process_efficiency']),
            "average_error_rate": float(recent_data['error_rate'].mean()),
            "total_downtime_30d": float(recent_data['downtime_hours'].sum()),
            "total_incidents_30d": int(recent_data['incidents_count'].sum()),
            "compliance_score": float(latest['compliance_score']),
            "vulnerability_count": vulnerabilities.get("total_count", 0),
            "operational_health_score": self._calculate_health_score(
                latest, recent_data, vulnerabilities
            )
        }
        
    def _calculate_health_score(
        self,
        latest: pd.Series,
        recent_data: pd.DataFrame,
        vulnerabilities: Dict[str, Any]
    ) -> float:
        """Расчет общего показателя здоровья операций"""
        # Нормализация метрик (0-1, где 1 = лучше)
        efficiency_score = latest['process_efficiency']
        error_score = 1 - min(latest['error_rate'] * 10, 1)  # Нормализация error_rate
        compliance_score = latest['compliance_score']
        
        # Штраф за уязвимости
        vulnerability_penalty = min(vulnerabilities.get("high_severity_count", 0) * 0.1, 0.3)
        
        health_score = (
            efficiency_score * 0.4 +
            error_score * 0.3 +
            compliance_score * 0.3
        ) - vulnerability_penalty
        
        return float(max(health_score, 0))
        
    async def _llm_operational_analysis(
        self,
        entity_id: Optional[str],
        process_data: pd.DataFrame,
        vulnerabilities: Dict[str, Any],
        log_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        LLM анализ операционного риска
        
        Args:
            entity_id: ID сущности
            process_data: Данные о процессах
            vulnerabilities: Уязвимости
            log_analysis: Анализ логов
            
        Returns:
            Результаты LLM анализа
        """
        if not self.llm_client:
            return {
                "analysis": "LLM analysis not available (no API keys configured)",
                "model": None
            }
            
        try:
            latest = process_data.iloc[-1]
            recent_data = process_data.tail(30)
            
            context = f"""
Операционные данные для {entity_id}:
- Эффективность процессов: {latest['process_efficiency']:.2%}
- Частота ошибок: {latest['error_rate']:.2%}
- Простои за 30 дней: {recent_data['downtime_hours'].sum():.1f} часов
- Инциденты за 30 дней: {recent_data['incidents_count'].sum()}
- Оценка соответствия: {latest['compliance_score']:.2%}
- Выявлено уязвимостей: {vulnerabilities.get('total_count', 0)}
"""
            
            prompt = f"""
Проанализируй операционные риски на основе следующих данных:

{context}

Предоставь:
1. Качественную оценку операционного риска
2. Основные проблемные области
3. Потенциальные последствия
4. Приоритетные рекомендации

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
        vulnerabilities: Dict[str, Any],
        failure_prediction: Dict[str, Any],
        operational_metrics: Dict[str, Any],
        llm_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Генерация рекомендаций
        
        Args:
            vulnerabilities: Уязвимости
            failure_prediction: Предсказания сбоев
            operational_metrics: Операционные метрики
            llm_analysis: LLM анализ
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Рекомендации на основе уязвимостей
        for vuln in vulnerabilities.get("vulnerabilities", []):
            if vuln["severity"] == "high":
                recommendations.append({
                    "priority": "high",
                    "category": "vulnerability",
                    "title": f"Устранение уязвимости: {vuln['type']}",
                    "description": vuln["recommendation"],
                    "impact": vuln["impact"]
                })
        
        # Рекомендации на основе предсказаний сбоев
        if failure_prediction.get("failure_probability_7d", 0) > 0.3:
            recommendations.append({
                "priority": "high",
                "category": "prevention",
                "title": "Проактивные меры для предотвращения сбоев",
                "description": f"Высокая вероятность сбоя ({failure_prediction['failure_probability_7d']:.1%}). Рекомендуется усилить мониторинг и подготовить план реагирования.",
                "impact": f"Ожидаемый ущерб: ${failure_prediction.get('expected_impact', 0):,.0f}"
            })
        
        # Рекомендации на основе метрик
        if operational_metrics.get("operational_health_score", 1) < 0.7:
            recommendations.append({
                "priority": "medium",
                "category": "improvement",
                "title": "Улучшение операционного здоровья",
                "description": f"Низкий показатель здоровья операций ({operational_metrics['operational_health_score']:.2%}). Рекомендуется комплексный аудит процессов.",
                "impact": "Повышение эффективности и снижение рисков"
            })
        
        return recommendations
        
    def _calculate_overall_risk_score(
        self,
        vulnerabilities: Dict[str, Any],
        failure_prediction: Dict[str, Any],
        operational_metrics: Dict[str, Any]
    ) -> float:
        """
        Расчет общего показателя операционного риска
        
        Args:
            vulnerabilities: Уязвимости
            failure_prediction: Предсказания сбоев
            operational_metrics: Операционные метрики
            
        Returns:
            Общий показатель риска (0-1, где 1 = максимальный риск)
        """
        # Компоненты риска
        vulnerability_score = min(
            vulnerabilities.get("high_severity_count", 0) * 0.2 +
            vulnerabilities.get("medium_severity_count", 0) * 0.1,
            0.5
        )
        
        failure_probability = failure_prediction.get("failure_probability_7d", 0)
        
        health_penalty = 1 - operational_metrics.get("operational_health_score", 1)
        
        # Взвешенная сумма
        overall_risk = (
            vulnerability_score * 0.3 +
            failure_probability * 0.4 +
            health_penalty * 0.3
        )
        
        return float(min(overall_risk, 1.0))
        
    async def _report_result(self, result: Dict[str, Any]):
        """Отчет о результатах анализа"""
        logger.info(f"Operational Risk Agent completed analysis for {result.get('entity_id')}")
        # TODO: Сохранение результатов в БД или отправка в Graph Builder
        pass

