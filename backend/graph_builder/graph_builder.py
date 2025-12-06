"""
ARIN Platform - Graph Builder
Построение и анализ графа зависимостей между финансовыми сущностями
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import networkx as nx
import numpy as np
from collections import defaultdict

from backend.config import settings

logger = logging.getLogger(__name__)


class GraphBuilder:
    """
    Построитель графа зависимостей
    
    Создает и обновляет граф зависимостей между:
    - Финансовыми институтами (банки, компании)
    - Секторами экономики
    - Географическими регионами
    - Типами активов
    - Контрагентами
    """
    
    def __init__(self):
        """Инициализация Graph Builder"""
        self.graph = nx.DiGraph()  # Направленный граф
        self.node_metadata = {}  # Метаданные узлов
        self.edge_metadata = {}  # Метаданные связей
        self.neo4j_driver = None  # Будет инициализирован при необходимости
        
    async def initialize(self):
        """Инициализация Graph Builder"""
        try:
            # TODO: Инициализация Neo4j если нужно
            # if settings.neo4j_url:
            #     from neo4j import GraphDatabase
            #     self.neo4j_driver = GraphDatabase.driver(
            #         settings.neo4j_url,
            #         auth=(settings.neo4j_user, settings.neo4j_password)
            #     )
            
            # Загрузка существующего графа если есть
            await self._load_existing_graph()
            
            logger.info("Graph Builder initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Graph Builder: {e}")
            raise
            
    async def _load_existing_graph(self):
        """Загрузка существующего графа из БД"""
        # TODO: Загрузка из Neo4j или PostgreSQL
        logger.info("Loading existing graph (placeholder)")
        
    def add_node(
        self,
        node_id: str,
        node_type: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Добавление узла в граф
        
        Args:
            node_id: Уникальный ID узла
            node_type: Тип узла (bank, company, sector, region, asset)
            properties: Дополнительные свойства узла
        """
        if properties is None:
            properties = {}
            
        self.graph.add_node(node_id, node_type=node_type, **properties)
        
        self.node_metadata[node_id] = {
            "node_type": node_type,
            "properties": properties,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        logger.debug(f"Added node: {node_id} (type: {node_type})")
        
    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        weight: Optional[float] = None,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Добавление связи в граф
        
        Args:
            source_id: ID исходного узла
            target_id: ID целевого узла
            relationship_type: Тип связи (credits, invests_in, operates_in, correlates_with)
            weight: Вес связи
            properties: Дополнительные свойства связи
        """
        if properties is None:
            properties = {}
            
        if weight is not None:
            properties["weight"] = weight
            
        self.graph.add_edge(
            source_id,
            target_id,
            relationship_type=relationship_type,
            **properties
        )
        
        edge_key = (source_id, target_id)
        self.edge_metadata[edge_key] = {
            "relationship_type": relationship_type,
            "weight": weight,
            "properties": properties,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        logger.debug(
            f"Added edge: {source_id} --[{relationship_type}]--> {target_id} "
            f"(weight: {weight})"
        )
        
    async def update_graph_from_risk_analysis(
        self,
        analysis_results: Dict[str, Any]
    ):
        """
        Обновление графа на основе результатов анализа рисков
        
        Args:
            analysis_results: Результаты анализа от агентов
        """
        try:
            agent_id = analysis_results.get("agent_id")
            entity_id = analysis_results.get("entity_id")
            entity_type = analysis_results.get("entity_type")
            
            # Добавление узла для сущности
            self.add_node(
                node_id=entity_id,
                node_type=entity_type,
                properties={
                    "risk_score": analysis_results.get("risk_score", 0),
                    "last_analysis": datetime.now().isoformat(),
                    "agent": agent_id
                }
            )
            
            # Добавление связей на основе анализа
            # Например, если Credit Risk Agent обнаружил зависимость от другой компании
            dependencies = analysis_results.get("dependencies", [])
            for dep in dependencies:
                self.add_edge(
                    source_id=entity_id,
                    target_id=dep.get("entity_id"),
                    relationship_type=dep.get("relationship_type", "depends_on"),
                    weight=dep.get("weight", 1.0),
                    properties=dep.get("properties", {})
                )
                
            logger.info(f"Graph updated from {agent_id} analysis for {entity_id}")
            
        except Exception as e:
            logger.error(f"Failed to update graph from risk analysis: {e}")
            
    async def find_influence_paths(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 3,
        max_paths: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Поиск путей влияния между узлами
        
        Args:
            source_id: ID исходного узла
            target_id: ID целевого узла
            max_depth: Максимальная глубина поиска
            max_paths: Максимальное количество путей
            
        Returns:
            Список путей влияния
        """
        if source_id not in self.graph or target_id not in self.graph:
            logger.warning(f"Nodes not found: {source_id} or {target_id}")
            return []
            
        try:
            # Поиск всех простых путей
            paths = list(nx.all_simple_paths(
                self.graph,
                source_id,
                target_id,
                cutoff=max_depth
            )[:max_paths])
            
            # Обогащение путей метаданными
            enriched_paths = []
            for path in paths:
                path_info = {
                    "path": path,
                    "length": len(path) - 1,
                    "nodes": [],
                    "edges": [],
                    "total_weight": 0.0,
                    "risk_propagation": self._calculate_risk_propagation(path)
                }
                
                # Добавление информации о узлах
                for node_id in path:
                    node_data = {
                        "node_id": node_id,
                        "node_type": self.graph.nodes[node_id].get("node_type"),
                        "properties": self.graph.nodes[node_id]
                    }
                    path_info["nodes"].append(node_data)
                    
                # Добавление информации о связях
                for i in range(len(path) - 1):
                    edge_data = self.graph[path[i]][path[i + 1]]
                    path_info["edges"].append({
                        "source": path[i],
                        "target": path[i + 1],
                        "relationship_type": edge_data.get("relationship_type"),
                        "weight": edge_data.get("weight", 1.0)
                    })
                    path_info["total_weight"] += edge_data.get("weight", 1.0)
                    
                enriched_paths.append(path_info)
                
            # Сортировка по длине и весу
            enriched_paths.sort(key=lambda x: (x["length"], -x["total_weight"]))
            
            logger.info(
                f"Found {len(enriched_paths)} paths from {source_id} to {target_id}"
            )
            
            return enriched_paths
            
        except nx.NetworkXNoPath:
            logger.info(f"No path found from {source_id} to {target_id}")
            return []
        except Exception as e:
            logger.error(f"Failed to find influence paths: {e}")
            return []
            
    def _calculate_risk_propagation(self, path: List[str]) -> float:
        """
        Расчет распространения риска по пути
        
        Args:
            path: Путь в графе
            
        Returns:
            Оценка распространения риска
        """
        total_risk = 0.0
        
        for node_id in path:
            node_risk = self.graph.nodes[node_id].get("risk_score", 0)
            total_risk += node_risk
            
        # Нормализация на длину пути
        return total_risk / len(path) if path else 0.0
        
    async def analyze_cascade_effects(
        self,
        source_id: str,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Анализ каскадных эффектов от узла
        
        Args:
            source_id: ID исходного узла
            max_depth: Максимальная глубина анализа
            
        Returns:
            Анализ каскадных эффектов
        """
        if source_id not in self.graph:
            return {"error": f"Node {source_id} not found"}
            
        try:
            # Поиск всех достижимых узлов
            reachable = nx.descendants(self.graph, source_id)
            
            # Группировка по глубине
            depth_groups = defaultdict(list)
            
            for target_id in reachable:
                try:
                    path_length = nx.shortest_path_length(
                        self.graph,
                        source_id,
                        target_id
                    )
                    if path_length <= max_depth:
                        depth_groups[path_length].append(target_id)
                except nx.NetworkXNoPath:
                    continue
                    
            # Расчет влияния на каждый уровень
            cascade_analysis = {
                "source_id": source_id,
                "source_risk": self.graph.nodes[source_id].get("risk_score", 0),
                "max_depth": max_depth,
                "affected_nodes": len(reachable),
                "depth_breakdown": {},
                "critical_paths": []
            }
            
            for depth, nodes in depth_groups.items():
                cascade_analysis["depth_breakdown"][depth] = {
                    "node_count": len(nodes),
                    "nodes": nodes,
                    "average_risk": self._calculate_average_risk(nodes)
                }
                
            # Поиск критических путей (с наибольшим влиянием)
            critical_paths = []
            for depth in range(1, min(max_depth + 1, 4)):
                for target_id in depth_groups.get(depth, []):
                    paths = await self.find_influence_paths(
                        source_id,
                        target_id,
                        max_depth=depth,
                        max_paths=3
                    )
                    if paths:
                        critical_paths.extend(paths[:1])  # Берем лучший путь
                        
            # Сортировка по риску
            critical_paths.sort(
                key=lambda x: x.get("risk_propagation", 0),
                reverse=True
            )
            cascade_analysis["critical_paths"] = critical_paths[:10]
            
            logger.info(
                f"Cascade analysis for {source_id}: "
                f"{len(reachable)} affected nodes, "
                f"{len(critical_paths)} critical paths"
            )
            
            return cascade_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze cascade effects: {e}")
            return {"error": str(e)}
            
    def _calculate_average_risk(self, node_ids: List[str]) -> float:
        """Расчет среднего риска для группы узлов"""
        risks = [
            self.graph.nodes[node_id].get("risk_score", 0)
            for node_id in node_ids
            if node_id in self.graph
        ]
        return np.mean(risks) if risks else 0.0
        
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Получение статистики графа
        
        Returns:
            Статистика графа
        """
        try:
            stats = {
                "nodes_count": self.graph.number_of_nodes(),
                "edges_count": self.graph.number_of_edges(),
                "node_types": defaultdict(int),
                "relationship_types": defaultdict(int),
                "density": nx.density(self.graph),
                "is_connected": nx.is_weakly_connected(self.graph),
                "components_count": nx.number_weakly_connected_components(self.graph)
            }
            
            # Подсчет типов узлов
            for node_id, data in self.graph.nodes(data=True):
                node_type = data.get("node_type", "unknown")
                stats["node_types"][node_type] += 1
                
            # Подсчет типов связей
            for source, target, data in self.graph.edges(data=True):
                rel_type = data.get("relationship_type", "unknown")
                stats["relationship_types"][rel_type] += 1
                
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get graph statistics: {e}")
            return {}
            
    async def get_graph_for_visualization(
        self,
        node_filter: Optional[List[str]] = None,
        max_nodes: int = 100
    ) -> Dict[str, Any]:
        """
        Получение данных графа для визуализации
        
        Args:
            node_filter: Фильтр узлов (если None, берет все)
            max_nodes: Максимальное количество узлов
            
        Returns:
            Данные для визуализации
        """
        try:
            # Фильтрация узлов
            if node_filter:
                subgraph = self.graph.subgraph(node_filter)
            else:
                # Берем узлы с наибольшим риском или связностью
                node_centrality = nx.degree_centrality(self.graph)
                top_nodes = sorted(
                    node_centrality.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:max_nodes]
                subgraph = self.graph.subgraph([node_id for node_id, _ in top_nodes])
                
            # Формирование данных для визуализации
            nodes = []
            for node_id, data in subgraph.nodes(data=True):
                nodes.append({
                    "id": node_id,
                    "type": data.get("node_type", "unknown"),
                    "label": node_id,
                    "risk_score": data.get("risk_score", 0),
                    "properties": {k: v for k, v in data.items() 
                                  if k not in ["node_type", "risk_score"]}
                })
                
            edges = []
            for source, target, data in subgraph.edges(data=True):
                edges.append({
                    "source": source,
                    "target": target,
                    "type": data.get("relationship_type", "unknown"),
                    "weight": data.get("weight", 1.0),
                    "properties": {k: v for k, v in data.items() 
                                  if k not in ["relationship_type", "weight"]}
                })
                
            return {
                "nodes": nodes,
                "edges": edges,
                "statistics": {
                    "nodes_count": len(nodes),
                    "edges_count": len(edges)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get graph for visualization: {e}")
            return {"nodes": [], "edges": []}
            
    async def save_to_database(self):
        """Сохранение графа в БД"""
        # TODO: Сохранение в Neo4j или PostgreSQL
        logger.info("Saving graph to database (placeholder)")
        
    async def detect_clusters(
        self,
        method: str = "louvain",
        min_cluster_size: int = 3
    ) -> Dict[str, Any]:
        """
        Обнаружение кластеров рисков
        
        Args:
            method: Метод кластеризации
            min_cluster_size: Минимальный размер кластера
            
        Returns:
            Результаты кластеризации
        """
        from backend.graph_builder.cluster_analyzer import ClusterAnalyzer
        
        analyzer = ClusterAnalyzer(self.graph)
        return await analyzer.detect_risk_clusters(method, min_cluster_size)
        
    async def find_risk_hotspots(
        self,
        min_risk_threshold: float = 0.7,
        min_cluster_size: int = 3
    ) -> Dict[str, Any]:
        """
        Поиск горячих точек риска
        
        Args:
            min_risk_threshold: Минимальный порог риска
            min_cluster_size: Минимальный размер кластера
            
        Returns:
            Горячие точки риска
        """
        from backend.graph_builder.cluster_analyzer import ClusterAnalyzer
        
        analyzer = ClusterAnalyzer(self.graph)
        return await analyzer.find_risk_hotspots(min_risk_threshold, min_cluster_size)
        
    async def get_graph_for_visualization_enhanced(
        self,
        node_filter: Optional[List[str]] = None,
        max_nodes: int = 100,
        include_clusters: bool = True
    ) -> Dict[str, Any]:
        """
        Получение данных графа для улучшенной визуализации
        
        Args:
            node_filter: Фильтр узлов
            max_nodes: Максимальное количество узлов
            include_clusters: Включить информацию о кластерах
            
        Returns:
            Данные для визуализации с кластерами
        """
        base_data = await self.get_graph_for_visualization(node_filter, max_nodes)
        
        if include_clusters:
            try:
                clusters_result = await self.detect_clusters(min_cluster_size=2)
                if "clusters" in clusters_result:
                    # Добавление информации о кластерах к узлам
                    cluster_mapping = {}
                    for cluster_id, nodes in clusters_result["clusters"].items():
                        for node_id in nodes:
                            cluster_mapping[node_id] = cluster_id
                    
                    # Обновление узлов с информацией о кластерах
                    for node in base_data["nodes"]:
                        node["cluster_id"] = cluster_mapping.get(node["id"])
                    
                    base_data["clusters"] = {
                        str(cluster_id): {
                            "nodes": nodes,
                            "risk_score": clusters_result["analysis"]["average_cluster_risk"].get(cluster_id, 0)
                        }
                        for cluster_id, nodes in clusters_result["clusters"].items()
                    }
            except Exception as e:
                logger.warning(f"Failed to add cluster information: {e}")
        
        return base_data
        
    async def shutdown(self):
        """Остановка Graph Builder"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
        logger.info("Graph Builder shut down")

