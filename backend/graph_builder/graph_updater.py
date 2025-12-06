"""
ARIN Platform - Graph Updater
Автоматическое обновление графа зависимостей
"""
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta

from backend.graph_builder.graph_builder import GraphBuilder
from backend.config import settings

logger = logging.getLogger(__name__)


class GraphUpdater:
    """
    Автоматическое обновление графа
    
    Обновляет граф на основе:
    - Результатов анализа агентов
    - Внешних источников данных
    - Изменений в финансовых данных
    """
    
    def __init__(self, graph_builder: GraphBuilder):
        """
        Инициализация Graph Updater
        
        Args:
            graph_builder: Экземпляр GraphBuilder
        """
        self.graph_builder = graph_builder
        self.update_interval = 300  # 5 минут
        self._running = False
        
    async def start(self):
        """Запуск автоматического обновления"""
        self._running = True
        logger.info("Graph Updater started")
        
        while self._running:
            try:
                await self._update_cycle()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in graph update cycle: {e}")
                await asyncio.sleep(60)  # Короткая задержка при ошибке
                
    async def stop(self):
        """Остановка автоматического обновления"""
        self._running = False
        logger.info("Graph Updater stopped")
        
    async def _update_cycle(self):
        """Цикл обновления графа"""
        try:
            logger.debug("Starting graph update cycle")
            
            # 1. Обновление на основе данных агентов
            # (будет вызываться через события от агентов)
            
            # 2. Обновление связей на основе новостей
            await self._update_from_news()
            
            # 3. Обновление весов связей
            await self._update_edge_weights()
            
            # 4. Обновление метрик узлов (центральность, риск)
            await self._update_node_metrics()
            
            # 5. Удаление устаревших узлов
            await self._cleanup_old_nodes()
            
            # 6. Сохранение в БД
            await self.graph_builder.save_to_database()
            
            logger.debug("Graph update cycle completed")
            
        except Exception as e:
            logger.error(f"Failed to update graph: {e}")
            
    async def _update_node_metrics(self):
        """Обновление метрик узлов (центральность, влияние)"""
        try:
            graph = self.graph_builder.graph
            
            # Расчет центральности
            degree_centrality = nx.degree_centrality(graph)
            betweenness_centrality = nx.betweenness_centrality(graph)
            closeness_centrality = nx.closeness_centrality(graph)
            
            # Обновление метаданных узлов
            for node_id in graph.nodes():
                if node_id not in self.graph_builder.node_metadata:
                    self.graph_builder.node_metadata[node_id] = {}
                
                self.graph_builder.node_metadata[node_id].update({
                    "degree_centrality": degree_centrality.get(node_id, 0),
                    "betweenness_centrality": betweenness_centrality.get(node_id, 0),
                    "closeness_centrality": closeness_centrality.get(node_id, 0),
                    "updated_at": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"Failed to update node metrics: {e}")
            
    async def _update_from_news(self):
        """Обновление графа на основе новостей"""
        # TODO: Интеграция с News Analytics Portal
        # Пока что placeholder
        pass
        
    async def _update_edge_weights(self):
        """Обновление весов связей на основе актуальных данных"""
        # TODO: Обновление весов на основе последних транзакций/данных
        pass
        
    async def _cleanup_old_nodes(self):
        """Удаление устаревших узлов"""
        # TODO: Удаление узлов, которые не обновлялись долгое время
        pass
        
    async def update_from_agent_result(self, agent_result: Dict[str, Any]):
        """
        Обновление графа на основе результата агента
        
        Args:
            agent_result: Результат анализа от агента
        """
        try:
            await self.graph_builder.update_graph_from_risk_analysis(agent_result)
        except Exception as e:
            logger.error(f"Failed to update graph from agent result: {e}")

