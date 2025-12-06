"""
ARIN Platform - Systemic Risk Agent
Агент для анализа системного риска и каскадных эффектов
"""
import logging
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from backend.agents.base_agent import BaseAgent, AgentStatus
from backend.config import settings
from backend.graph_builder.graph_builder import GraphBuilder
import networkx as nx

logger = logging.getLogger(__name__)


class SystemicRiskAgent(BaseAgent):
    """Агент для анализа системного риска"""
    
    def __init__(self, agent_id: str = "systemic_risk_agent", config: Optional[Dict[str, Any]] = None):
        """
        Инициализация Systemic Risk Agent
        
        Args:
            agent_id: ID агента
            config: Конфигурация агента
        """
        if config is None:
            config = {}
            
        super().__init__(
            agent_id=agent_id,
            agent_name="Systemic Risk Agent",
            config=config
        )
        
        self.db_engine = None
        self.graph_builder = None
        self.other_agents = {}  # Ссылки на другие агенты для получения данных
        self.gnn_predictor = None  # GNN модель для предсказания влияния
        
    async def _setup_data_access(self):
        """Настройка доступа к данным"""
        try:
            # TODO: Настроить подключение к БД
            # from sqlalchemy import create_engine
            # self.db_engine = create_engine(settings.database_url)
            
            # Интеграция с Graph Builder для анализа взаимосвязей
            # Graph Builder должен быть инициализирован в main.py
            logger.info("Systemic Risk Agent will use Graph Builder for dependency analysis")
                
            logger.info("Systemic Risk Agent data access setup completed")
        except Exception as e:
            logger.error(f"Failed to setup data access: {e}")
            raise
            
    async def _setup_ai_integration(self):
        """Настройка AI интеграции"""
        try:
            # Загрузка GNN модели для предсказания влияния
            await self._load_gnn_model()
            
            logger.info("Systemic Risk Agent AI integration setup completed")
        except Exception as e:
            logger.error(f"Failed to setup AI integration: {e}")
            raise
            
    async def _load_gnn_model(self):
        """Загрузка GNN модели"""
        try:
            from pathlib import Path
            from backend.ai_engine.ml_models.gnn_model import GNNPredictor
            
            # Путь к модели
            model_path = Path(__file__).parent.parent / "models" / "gnn_model.pth"
            
            if model_path.exists():
                self.gnn_predictor = GNNPredictor(model_path=str(model_path))
                logger.info(f"GNN model loaded from {model_path}")
            else:
                logger.info(f"GNN model not found at {model_path}. Will use graph-based analysis only.")
                self.gnn_predictor = None
                
        except Exception as e:
            logger.warning(f"Failed to load GNN model: {e}")
            self.gnn_predictor = None
            
    def set_graph_builder(self, graph_builder: GraphBuilder):
        """Установка Graph Builder для анализа зависимостей"""
        self.graph_builder = graph_builder
        
    def set_other_agents(self, agents: Dict[str, BaseAgent]):
        """Установка ссылок на другие агенты для получения данных"""
        self.other_agents = agents
        
    async def analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ системного риска
        
        Args:
            task: Задача для анализа
                - entity_id: ID сущности (портфель, система)
                - entity_type: Тип сущности
                - parameters: Дополнительные параметры
                
        Returns:
            Результаты анализа системного риска
        """
        entity_id = task.get("entity_id")
        entity_type = task.get("entity_type", "portfolio")
        parameters = task.get("parameters", {})
        
        logger.info(f"Analyzing systemic risk for {entity_type} {entity_id}")
        
        try:
            # 1. Получение данных от других агентов
            agent_data = await self._collect_agent_data(entity_id, parameters)
            
            # 2. Анализ системных взаимосвязей через Graph Builder
            systemic_connections = await self._analyze_systemic_connections(entity_id, parameters)
            
            # 3. Выявление каскадных эффектов
            cascade_effects = await self._identify_cascade_effects(entity_id, agent_data, systemic_connections)
            
            # 4. Анализ концентрации рисков
            concentration_analysis = await self._analyze_concentration(entity_id, agent_data)
            
            # 5. Анализ корреляций между рисками
            correlation_analysis = await self._analyze_risk_correlations(agent_data)
            
            # 6. Стресс-тестирование системных рисков
            systemic_stress_test = await self._systemic_stress_test(
                entity_id, agent_data, systemic_connections
            )
            
            # 7. Генерация рекомендаций
            recommendations = await self._generate_recommendations(
                cascade_effects, concentration_analysis, correlation_analysis, systemic_stress_test
            )
            
            result = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "timestamp": datetime.now().isoformat(),
                "agent_data": agent_data,
                "systemic_connections": systemic_connections,
                "cascade_effects": cascade_effects,
                "concentration_analysis": concentration_analysis,
                "correlation_analysis": correlation_analysis,
                "systemic_stress_test": systemic_stress_test,
                "recommendations": recommendations,
                "risk_score": self._calculate_overall_risk_score(
                    cascade_effects, concentration_analysis, correlation_analysis, systemic_stress_test
                )
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze systemic risk: {e}")
            raise
            
    async def _collect_agent_data(
        self, 
        entity_id: Optional[str], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Сбор данных от других агентов
        
        Args:
            entity_id: ID сущности
            parameters: Параметры
            
        Returns:
            Данные от всех агентов
        """
        agent_data = {}
        
        # Создаем задачу для каждого агента
        task = {
            "task_id": f"systemic_analysis_{entity_id}_{datetime.now().isoformat()}",
            "entity_id": entity_id,
            "entity_type": parameters.get("entity_type", "portfolio"),
            "parameters": parameters
        }
        
        # Собираем данные от каждого агента
        for agent_id, agent in self.other_agents.items():
            if agent_id == self.agent_id:
                continue  # Пропускаем себя
                
            try:
                result = await agent.analyze(task)
                agent_data[agent_id] = {
                    "risk_score": result.get("risk_score", 0),
                    "status": "completed",
                    "data": result
                }
            except Exception as e:
                logger.warning(f"Failed to get data from {agent_id}: {e}")
                agent_data[agent_id] = {
                    "risk_score": None,
                    "status": "failed",
                    "error": str(e)
                }
        
        return agent_data
        
    async def _analyze_systemic_connections(
        self, 
        entity_id: Optional[str], 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ системных взаимосвязей
        
        Args:
            entity_id: ID сущности
            parameters: Параметры
            
        Returns:
            Анализ системных взаимосвязей
        """
        if not self.graph_builder:
            return {
                "connections": [],
                "note": "Graph Builder not available"
            }
        
        try:
            connections = []
            
            if entity_id and entity_id in self.graph_builder.graph:
                # Использование GNN для предсказания влияния
                if self.gnn_predictor:
                    try:
                        # Предсказание влияния на все узлы
                        graph = self.graph_builder.graph
                        predictions = self.gnn_predictor.predict_influence(
                            graph=graph,
                            source_node=entity_id
                        )
                        
                        # Формирование списка связей с предсказанным влиянием
                        for target_id, influence_score in predictions.items():
                            if influence_score > 0.1:  # Порог значимости
                                connections.append({
                                    "target": target_id,
                                    "strength": float(influence_score),
                                    "method": "gnn_prediction"
                                })
                    except Exception as e:
                        logger.warning(f"GNN prediction failed: {e}, using graph-based analysis")
                
                # Fallback: анализ через Graph Builder
                if not connections:
                    # Поиск всех достижимых узлов
                    graph = self.graph_builder.graph
                    if entity_id in graph:
                        reachable = list(nx.descendants(graph, entity_id))
                        for target_id in reachable[:50]:  # Ограничение для производительности
                            try:
                                paths = await self.graph_builder.find_influence_paths(
                                    entity_id, target_id, max_depth=3, max_paths=1
                                )
                                if paths:
                                    path = paths[0]
                                    strength = 1.0 / (path.get("length", 1) + 1)  # Обратная зависимость от длины
                                    connections.append({
                                        "target": target_id,
                                        "strength": strength,
                                        "method": "graph_analysis"
                                    })
                            except Exception:
                                continue
            
            return {
                "connections": connections,
                "total_connections": len(connections),
                "strong_connections": sum(1 for c in connections if c.get("strength", 0) > 0.7),
                "weak_connections": sum(1 for c in connections if c.get("strength", 0) < 0.3),
                "gnn_used": self.gnn_predictor is not None
            }
        except Exception as e:
            logger.error(f"Failed to analyze systemic connections: {e}")
            return {
                "connections": [],
                "error": str(e)
            }
        
    async def _identify_cascade_effects(
        self, 
        entity_id: Optional[str],
        agent_data: Dict[str, Any],
        systemic_connections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Выявление каскадных эффектов
        
        Args:
            entity_id: ID сущности
            agent_data: Данные от агентов
            systemic_connections: Системные взаимосвязи
            
        Returns:
            Каскадные эффекты
        """
        cascade_effects = []
        
        # Анализ рисков от каждого агента
        high_risk_agents = [
            agent_id for agent_id, data in agent_data.items()
            if data.get("risk_score") and data.get("risk_score", 0) > 0.7
        ]
        
        # Поиск потенциальных каскадных эффектов
        for high_risk_agent in high_risk_agents:
            # Анализ влияния на другие агенты
            affected_agents = []
            for other_agent_id, other_data in agent_data.items():
                if other_agent_id != high_risk_agent:
                    # Упрощенная логика: высокий риск в одном агенте увеличивает риск в других
                    if other_data.get("risk_score", 0) > 0.5:
                        affected_agents.append({
                            "agent_id": other_agent_id,
                            "cascade_probability": 0.6,
                            "impact": "medium"
                        })
            
            if affected_agents:
                cascade_effects.append({
                    "source_agent": high_risk_agent,
                    "source_risk_score": agent_data[high_risk_agent].get("risk_score", 0),
                    "affected_agents": affected_agents,
                    "cascade_severity": "high" if len(affected_agents) > 2 else "medium"
                })
        
        return {
            "cascade_effects": cascade_effects,
            "total_cascades": len(cascade_effects),
            "high_severity_cascades": sum(1 for c in cascade_effects if c["cascade_severity"] == "high"),
            "potential_impact": "high" if len(cascade_effects) > 0 else "low"
        }
        
    async def _analyze_concentration(
        self, 
        entity_id: Optional[str], 
        agent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ концентрации рисков
        
        Args:
            entity_id: ID сущности
            agent_data: Данные от агентов
            
        Returns:
            Анализ концентрации
        """
        # Извлечение показателей риска
        risk_scores = [
            data.get("risk_score", 0) 
            for data in agent_data.values() 
            if data.get("risk_score") is not None
        ]
        
        if not risk_scores:
            return {
                "concentration_score": 0,
                "risk_level": "low",
                "note": "No risk data available"
            }
        
        # Расчет концентрации (HHI - Herfindahl-Hirschman Index)
        normalized_scores = np.array(risk_scores) / sum(risk_scores) if sum(risk_scores) > 0 else np.array(risk_scores)
        hhi = np.sum(normalized_scores ** 2)
        
        # Оценка концентрации
        if hhi > 0.5:
            concentration_level = "high"
        elif hhi > 0.3:
            concentration_level = "medium"
        else:
            concentration_level = "low"
        
        # Максимальный риск
        max_risk = max(risk_scores)
        max_risk_agent = [
            agent_id for agent_id, data in agent_data.items()
            if data.get("risk_score") == max_risk
        ][0] if risk_scores else None
        
        return {
            "concentration_score": float(hhi),
            "concentration_level": concentration_level,
            "max_risk_score": float(max_risk),
            "max_risk_agent": max_risk_agent,
            "risk_distribution": {
                "high_risk_count": sum(1 for r in risk_scores if r > 0.7),
                "medium_risk_count": sum(1 for r in risk_scores if 0.4 < r <= 0.7),
                "low_risk_count": sum(1 for r in risk_scores if r <= 0.4)
            }
        }
        
    async def _analyze_risk_correlations(
        self, 
        agent_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ корреляций между рисками
        
        Args:
            agent_data: Данные от агентов
            
        Returns:
            Анализ корреляций
        """
        # Извлечение временных рядов рисков (упрощенно)
        # В реальности нужны исторические данные
        
        agent_ids = list(agent_data.keys())
        risk_scores = [
            agent_data[agent_id].get("risk_score", 0)
            for agent_id in agent_ids
            if agent_data[agent_id].get("risk_score") is not None
        ]
        
        if len(risk_scores) < 2:
            return {
                "correlations": {},
                "average_correlation": 0,
                "note": "Insufficient data for correlation analysis"
            }
        
        # Упрощенный расчет корреляций
        # В реальности нужны временные ряды
        correlations = {}
        for i, agent_id_1 in enumerate(agent_ids):
            for j, agent_id_2 in enumerate(agent_ids):
                if i < j:
                    # Упрощенная корреляция на основе текущих значений
                    score_1 = agent_data[agent_id_1].get("risk_score", 0)
                    score_2 = agent_data[agent_id_2].get("risk_score", 0)
                    
                    # Простая метрика схожести
                    correlation = 1 - abs(score_1 - score_2)
                    correlations[f"{agent_id_1}_{agent_id_2}"] = float(correlation)
        
        avg_correlation = np.mean(list(correlations.values())) if correlations else 0
        
        return {
            "correlations": correlations,
            "average_correlation": float(avg_correlation),
            "high_correlation_pairs": [
                pair for pair, corr in correlations.items()
                if corr > 0.7
            ]
        }
        
    async def _systemic_stress_test(
        self,
        entity_id: Optional[str],
        agent_data: Dict[str, Any],
        systemic_connections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Стресс-тестирование системных рисков
        
        Args:
            entity_id: ID сущности
            agent_data: Данные от агентов
            systemic_connections: Системные взаимосвязи
            
        Returns:
            Результаты стресс-теста
        """
        scenarios = {
            "market_shock": {
                "description": "Рыночный шок",
                "impact": {
                    "market_risk_agent": 0.3,  # +30% к риску
                    "credit_risk_agent": 0.15,
                    "liquidity_risk_agent": 0.20
                }
            },
            "credit_crisis": {
                "description": "Кредитный кризис",
                "impact": {
                    "credit_risk_agent": 0.4,
                    "market_risk_agent": 0.25,
                    "liquidity_risk_agent": 0.30
                }
            },
            "operational_failure": {
                "description": "Операционный сбой",
                "impact": {
                    "operational_risk_agent": 0.5,
                    "liquidity_risk_agent": 0.20,
                    "market_risk_agent": 0.10
                }
            }
        }
        
        stress_results = {}
        for scenario_name, scenario in scenarios.items():
            # Применение шоков к рискам
            stressed_risks = {}
            for agent_id, data in agent_data.items():
                base_risk = data.get("risk_score", 0)
                shock = scenario["impact"].get(agent_id, 0)
                stressed_risk = min(base_risk + shock, 1.0)
                stressed_risks[agent_id] = stressed_risk
            
            # Расчет системного риска в стресс-сценарии
            systemic_risk = np.mean(list(stressed_risks.values()))
            
            stress_results[scenario_name] = {
                "description": scenario["description"],
                "stressed_risks": stressed_risks,
                "systemic_risk_score": float(systemic_risk),
                "worst_affected_agent": max(stressed_risks.items(), key=lambda x: x[1])[0] if stressed_risks else None
            }
        
        return {
            "scenarios": stress_results,
            "worst_case": max(
                stress_results.values(),
                key=lambda x: x["systemic_risk_score"]
            )
        }
        
    async def _generate_recommendations(
        self,
        cascade_effects: Dict[str, Any],
        concentration_analysis: Dict[str, Any],
        correlation_analysis: Dict[str, Any],
        systemic_stress_test: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Генерация рекомендаций
        
        Args:
            cascade_effects: Каскадные эффекты
            concentration_analysis: Анализ концентрации
            correlation_analysis: Анализ корреляций
            systemic_stress_test: Стресс-тест
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        # Рекомендации по каскадным эффектам
        if cascade_effects.get("total_cascades", 0) > 0:
            recommendations.append({
                "priority": "high",
                "category": "cascade",
                "title": "Обнаружены потенциальные каскадные эффекты",
                "description": f"Выявлено {cascade_effects['total_cascades']} потенциальных каскадных эффектов. Рекомендуется усилить мониторинг взаимосвязей.",
                "impact": "Снижение системного риска"
            })
        
        # Рекомендации по концентрации
        if concentration_analysis.get("concentration_level") == "high":
            recommendations.append({
                "priority": "high",
                "category": "concentration",
                "title": "Высокая концентрация рисков",
                "description": f"Концентрация рисков высокая (HHI: {concentration_analysis['concentration_score']:.2f}). Рекомендуется диверсификация.",
                "impact": "Снижение концентрации и системного риска"
            })
        
        # Рекомендации по корреляциям
        if correlation_analysis.get("average_correlation", 0) > 0.7:
            recommendations.append({
                "priority": "medium",
                "category": "correlation",
                "title": "Высокая корреляция между рисками",
                "description": "Риски сильно коррелируют между собой. Рекомендуется анализ независимых источников риска.",
                "impact": "Повышение устойчивости к системным шокам"
            })
        
        # Рекомендации по стресс-тесту
        worst_case = systemic_stress_test.get("worst_case", {})
        if worst_case.get("systemic_risk_score", 0) > 0.8:
            recommendations.append({
                "priority": "high",
                "category": "stress_test",
                "title": "Уязвимость в стресс-сценариях",
                "description": f"В стресс-сценарии системный риск достигает {worst_case['systemic_risk_score']:.2%}. Рекомендуется усилить буферы.",
                "impact": "Повышение устойчивости к системным кризисам"
            })
        
        return recommendations
        
    def _calculate_overall_risk_score(
        self,
        cascade_effects: Dict[str, Any],
        concentration_analysis: Dict[str, Any],
        correlation_analysis: Dict[str, Any],
        systemic_stress_test: Dict[str, Any]
    ) -> float:
        """
        Расчет общего показателя системного риска
        
        Args:
            cascade_effects: Каскадные эффекты
            concentration_analysis: Анализ концентрации
            correlation_analysis: Анализ корреляций
            systemic_stress_test: Стресс-тест
            
        Returns:
            Общий показатель риска (0-1, где 1 = максимальный риск)
        """
        # Компоненты риска
        cascade_risk = min(cascade_effects.get("total_cascades", 0) * 0.15, 0.4)
        
        concentration_risk = 0.0
        if concentration_analysis.get("concentration_level") == "high":
            concentration_risk = 0.3
        elif concentration_analysis.get("concentration_level") == "medium":
            concentration_risk = 0.15
        
        correlation_risk = correlation_analysis.get("average_correlation", 0) * 0.2
        
        stress_risk = systemic_stress_test.get("worst_case", {}).get("systemic_risk_score", 0) * 0.3
        
        # Взвешенная сумма
        overall_risk = (
            cascade_risk * 0.25 +
            concentration_risk * 0.25 +
            correlation_risk * 0.2 +
            stress_risk * 0.3
        )
        
        return float(min(overall_risk, 1.0))
        
    async def _report_result(self, result: Dict[str, Any]):
        """Отчет о результатах анализа"""
        logger.info(f"Systemic Risk Agent completed analysis for {result.get('entity_id')}")
        # TODO: Сохранение результатов в БД или отправка в Graph Builder
        pass

