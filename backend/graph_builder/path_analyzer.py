"""
ARIN Platform - Path Analyzer
Анализ путей влияния в графе зависимостей
"""
import logging
from typing import Dict, Any, List, Optional
import networkx as nx

from backend.graph_builder.graph_builder import GraphBuilder

logger = logging.getLogger(__name__)


class PathAnalyzer:
    """
    Анализатор путей влияния
    
    Находит и анализирует пути влияния между узлами в графе
    """
    
    def __init__(self, graph_builder: GraphBuilder):
        """
        Инициализация Path Analyzer
        
        Args:
            graph_builder: Экземпляр GraphBuilder
        """
        self.graph_builder = graph_builder
        
    async def find_all_paths(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Поиск всех путей между узлами
        
        Args:
            source_id: ID исходного узла
            target_id: ID целевого узла
            max_depth: Максимальная глубина
            
        Returns:
            Список всех путей
        """
        return await self.graph_builder.find_influence_paths(
            source_id, target_id, max_depth
        )
        
    async def find_shortest_path(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Поиск кратчайшего пути
        
        Args:
            source_id: ID исходного узла
            target_id: ID целевого узла
            
        Returns:
            Кратчайший путь или None
        """
        paths = await self.find_all_paths(source_id, target_id, max_depth=10)
        if paths:
            return paths[0]  # Первый путь - кратчайший
        return None
        
    async def find_critical_paths(
        self,
        source_id: str,
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Поиск критических путей от узла
        
        Args:
            source_id: ID исходного узла
            max_depth: Максимальная глубина
            
        Returns:
            Список критических путей
        """
        cascade = await self.graph_builder.analyze_cascade_effects(
            source_id, max_depth
        )
        return cascade.get("critical_paths", [])
        
    async def analyze_path_risk(
        self,
        path: List[str]
    ) -> Dict[str, Any]:
        """
        Анализ риска пути
        
        Args:
            path: Путь в графе
            
        Returns:
            Анализ риска пути
        """
        graph = self.graph_builder.graph
        
        if not all(node_id in graph for node_id in path):
            return {"error": "Invalid path"}
            
        # Расчет метрик пути
        total_risk = sum(
            graph.nodes[node_id].get("risk_score", 0)
            for node_id in path
        )
        
        avg_risk = total_risk / len(path) if path else 0
        
        # Расчет веса пути
        total_weight = 0.0
        for i in range(len(path) - 1):
            edge_data = graph[path[i]][path[i + 1]]
            total_weight += edge_data.get("weight", 1.0)
            
        return {
            "path": path,
            "length": len(path) - 1,
            "total_risk": total_risk,
            "average_risk": avg_risk,
            "total_weight": total_weight,
            "risk_propagation": self.graph_builder._calculate_risk_propagation(path)
        }

