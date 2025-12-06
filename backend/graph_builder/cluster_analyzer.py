"""
ARIN Platform - Cluster Analyzer
Обнаружение кластеров рисков в графе зависимостей
"""
import logging
from typing import Dict, Any, List, Optional
import networkx as nx
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class ClusterAnalyzer:
    """
    Анализатор кластеров рисков
    
    Обнаруживает кластеры (сообщества) в графе зависимостей
    для выявления групп взаимосвязанных рисков
    """
    
    def __init__(self, graph: nx.DiGraph):
        """
        Инициализация Cluster Analyzer
        
        Args:
            graph: Граф зависимостей
        """
        self.graph = graph
        
    async def detect_risk_clusters(
        self,
        method: str = "louvain",
        min_cluster_size: int = 3
    ) -> Dict[str, Any]:
        """
        Обнаружение кластеров рисков
        
        Args:
            method: Метод кластеризации (louvain, leiden, k_clique)
            min_cluster_size: Минимальный размер кластера
            
        Returns:
            Результаты кластеризации
        """
        try:
            if method == "louvain":
                clusters = await self._louvain_clustering()
            elif method == "leiden":
                clusters = await self._leiden_clustering()
            elif method == "k_clique":
                clusters = await self._k_clique_clustering()
            else:
                clusters = await self._louvain_clustering()
            
            # Фильтрация по минимальному размеру
            filtered_clusters = {
                cluster_id: nodes
                for cluster_id, nodes in clusters.items()
                if len(nodes) >= min_cluster_size
            }
            
            # Анализ кластеров
            cluster_analysis = await self._analyze_clusters(filtered_clusters)
            
            return {
                "clusters": filtered_clusters,
                "cluster_count": len(filtered_clusters),
                "total_nodes_in_clusters": sum(len(nodes) for nodes in filtered_clusters.values()),
                "analysis": cluster_analysis,
                "method": method
            }
            
        except Exception as e:
            logger.error(f"Failed to detect risk clusters: {e}")
            return {"error": str(e)}
            
    async def _louvain_clustering(self) -> Dict[int, List[str]]:
        """
        Кластеризация методом Louvain
        
        Returns:
            Словарь {cluster_id: [node_ids]}
        """
        try:
            # Преобразование в неориентированный граф для Louvain
            undirected = self.graph.to_undirected()
            
            # Использование алгоритма Louvain через networkx
            # Если нет community detection, используем простой алгоритм
            try:
                import networkx.algorithms.community as nx_comm
                communities = nx_comm.louvain_communities(undirected, seed=42)
            except (ImportError, AttributeError):
                # Fallback: простой алгоритм на основе связности
                communities = list(nx.connected_components(undirected))
            
            clusters = {}
            for i, community in enumerate(communities):
                clusters[i] = list(community)
                
            return clusters
            
        except Exception as e:
            logger.error(f"Louvain clustering failed: {e}")
            return {}
            
    async def _leiden_clustering(self) -> Dict[int, List[str]]:
        """
        Кластеризация методом Leiden
        
        Returns:
            Словарь {cluster_id: [node_ids]}
        """
        try:
            # Leiden требует дополнительной библиотеки
            # Fallback на Louvain
            return await self._louvain_clustering()
            
        except Exception as e:
            logger.error(f"Leiden clustering failed: {e}")
            return {}
            
    async def _k_clique_clustering(self, k: int = 3) -> Dict[int, List[str]]:
        """
        Кластеризация методом k-clique
        
        Args:
            k: Размер клики
            
        Returns:
            Словарь {cluster_id: [node_ids]}
        """
        try:
            undirected = self.graph.to_undirected()
            
            # Поиск всех k-клик
            cliques = list(nx.find_cliques(undirected))
            k_cliques = [clique for clique in cliques if len(clique) >= k]
            
            # Объединение пересекающихся клик
            clusters = {}
            cluster_id = 0
            used_nodes = set()
            
            for clique in k_cliques:
                # Проверка пересечения с существующими кластерами
                clique_set = set(clique)
                if clique_set & used_nodes:
                    # Добавляем к существующему кластеру
                    for cid, nodes in clusters.items():
                        if clique_set & set(nodes):
                            clusters[cid].extend([n for n in clique if n not in clusters[cid]])
                            used_nodes.update(clique)
                            break
                else:
                    # Создаем новый кластер
                    clusters[cluster_id] = list(clique)
                    used_nodes.update(clique)
                    cluster_id += 1
            
            return clusters
            
        except Exception as e:
            logger.error(f"K-clique clustering failed: {e}")
            return {}
            
    async def _analyze_clusters(
        self,
        clusters: Dict[int, List[str]]
    ) -> Dict[str, Any]:
        """
        Анализ обнаруженных кластеров
        
        Args:
            clusters: Словарь кластеров
            
        Returns:
            Анализ кластеров
        """
        analysis = {
            "cluster_metrics": {},
            "high_risk_clusters": [],
            "cluster_types": defaultdict(list),
            "average_cluster_risk": {}
        }
        
        for cluster_id, nodes in clusters.items():
            # Метрики кластера
            cluster_risk = self._calculate_cluster_risk(nodes)
            cluster_density = self._calculate_cluster_density(nodes)
            cluster_size = len(nodes)
            
            # Типы узлов в кластере
            node_types = defaultdict(int)
            for node_id in nodes:
                if node_id in self.graph:
                    node_type = self.graph.nodes[node_id].get("node_type", "unknown")
                    node_types[node_type] += 1
            
            analysis["cluster_metrics"][cluster_id] = {
                "size": cluster_size,
                "risk_score": cluster_risk,
                "density": cluster_density,
                "node_types": dict(node_types)
            }
            
            analysis["average_cluster_risk"][cluster_id] = cluster_risk
            
            # Высокорисковые кластеры
            if cluster_risk > 0.7:
                analysis["high_risk_clusters"].append({
                    "cluster_id": cluster_id,
                    "risk_score": cluster_risk,
                    "size": cluster_size,
                    "nodes": nodes
                })
            
            # Классификация по преобладающему типу
            dominant_type = max(node_types.items(), key=lambda x: x[1])[0] if node_types else "unknown"
            analysis["cluster_types"][dominant_type].append(cluster_id)
        
        return analysis
        
    def _calculate_cluster_risk(self, nodes: List[str]) -> float:
        """Расчет среднего риска кластера"""
        risks = [
            self.graph.nodes[node_id].get("risk_score", 0)
            for node_id in nodes
            if node_id in self.graph
        ]
        return float(np.mean(risks)) if risks else 0.0
        
    def _calculate_cluster_density(self, nodes: List[str]) -> float:
        """Расчет плотности кластера"""
        if len(nodes) < 2:
            return 0.0
            
        subgraph = self.graph.subgraph(nodes)
        undirected = subgraph.to_undirected()
        
        # Плотность = количество ребер / максимальное возможное количество
        edges = undirected.number_of_edges()
        max_edges = len(nodes) * (len(nodes) - 1) / 2
        
        return float(edges / max_edges) if max_edges > 0 else 0.0
        
    async def find_risk_hotspots(
        self,
        min_risk_threshold: float = 0.7,
        min_cluster_size: int = 3
    ) -> Dict[str, Any]:
        """
        Поиск "горячих точек" риска (высокорисковые кластеры)
        
        Args:
            min_risk_threshold: Минимальный порог риска
            min_cluster_size: Минимальный размер кластера
            
        Returns:
            Горячие точки риска
        """
        clusters_result = await self.detect_risk_clusters(min_cluster_size=min_cluster_size)
        
        if "error" in clusters_result:
            return clusters_result
        
        hotspots = []
        for cluster_id, nodes in clusters_result["clusters"].items():
            cluster_risk = clusters_result["analysis"]["average_cluster_risk"].get(cluster_id, 0)
            
            if cluster_risk >= min_risk_threshold:
                hotspots.append({
                    "cluster_id": cluster_id,
                    "nodes": nodes,
                    "risk_score": cluster_risk,
                    "size": len(nodes),
                    "density": clusters_result["analysis"]["cluster_metrics"][cluster_id]["density"]
                })
        
        return {
            "hotspots": hotspots,
            "hotspot_count": len(hotspots),
            "total_nodes_in_hotspots": sum(h["size"] for h in hotspots),
            "average_hotspot_risk": float(np.mean([h["risk_score"] for h in hotspots])) if hotspots else 0.0
        }

