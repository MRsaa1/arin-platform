"""
ARIN Platform - Graph API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel

# Lazy import to avoid circular dependency
def get_graph_builder():
    from backend.main import graph_builder_instance
    return graph_builder_instance

router = APIRouter()

# Get graph_builder_instance at module level
graph_builder_instance = None


class GraphNodeRequest(BaseModel):
    """Запрос на добавление узла"""
    node_id: str
    node_type: str
    properties: Optional[dict] = None


class GraphEdgeRequest(BaseModel):
    """Запрос на добавление связи"""
    source_id: str
    target_id: str
    relationship_type: str
    weight: Optional[float] = None
    properties: Optional[dict] = None


@router.get("")
async def get_graph(
    max_nodes: int = Query(100, description="Maximum number of nodes"),
    node_filter: Optional[List[str]] = Query(None, description="Filter nodes by IDs")
):
    """Получить граф зависимостей"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        graph_data = await graph_builder.get_graph_for_visualization(
            node_filter=node_filter,
            max_nodes=max_nodes
        )
        return graph_data
    except Exception as e:
        import logging
        logging.error(f"Error getting graph: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paths")
async def find_paths(
    source: str = Query(..., description="Source node ID"),
    target: str = Query(..., description="Target node ID"),
    max_depth: int = Query(3, description="Maximum path depth")
):
    """Найти пути влияния между узлами"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        paths = await graph_builder.find_influence_paths(
            source, target, max_depth=max_depth
        )
        return {"paths": paths}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cascade")
async def analyze_cascade(
    source: str = Query(..., description="Source node ID"),
    max_depth: int = Query(3, description="Maximum cascade depth")
):
    """Анализ каскадных эффектов от узла"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        cascade = await graph_builder.analyze_cascade_effects(
            source, max_depth=max_depth
        )
        return cascade
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_graph_statistics():
    """Получить статистику графа"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        stats = await graph_builder.get_graph_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/nodes")
async def add_node(request: GraphNodeRequest):
    """Добавить узел в граф"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        graph_builder.add_node(
            node_id=request.node_id,
            node_type=request.node_type,
            properties=request.properties
        )
        return {"message": f"Node {request.node_id} added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/edges")
async def add_edge(request: GraphEdgeRequest):
    """Добавить связь в граф"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        graph_builder.add_edge(
            source_id=request.source_id,
            target_id=request.target_id,
            relationship_type=request.relationship_type,
            weight=request.weight,
            properties=request.properties
        )
        return {"message": f"Edge {request.source_id} -> {request.target_id} added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters")
async def detect_clusters(
    method: str = Query("louvain", description="Clustering method"),
    min_cluster_size: int = Query(3, description="Minimum cluster size")
):
    """Обнаружить кластеры рисков в графе"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        clusters = await graph_builder.detect_clusters(
            method=method,
            min_cluster_size=min_cluster_size
        )
        return clusters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hotspots")
async def find_hotspots(
    min_risk_threshold: float = Query(0.7, description="Minimum risk threshold"),
    min_cluster_size: int = Query(3, description="Minimum cluster size")
):
    """Найти горячие точки риска"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        hotspots = await graph_builder.find_risk_hotspots(
            min_risk_threshold=min_risk_threshold,
            min_cluster_size=min_cluster_size
        )
        return hotspots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/visualization")
async def get_graph_visualization(
    max_nodes: int = Query(100, description="Maximum number of nodes"),
    node_filter: Optional[List[str]] = Query(None, description="Filter nodes by IDs"),
    include_clusters: bool = Query(True, description="Include cluster information")
):
    """Получить граф для улучшенной визуализации с кластерами"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        graph_data = await graph_builder.get_graph_for_visualization_enhanced(
            node_filter=node_filter,
            max_nodes=max_nodes,
            include_clusters=include_clusters
        )
        return graph_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def update_graph():
    """Обновить граф зависимостей"""
    graph_builder = get_graph_builder()
    if not graph_builder:
        raise HTTPException(status_code=503, detail="Graph Builder not initialized")
    
    try:
        await graph_builder.save_to_database()
        return {"message": "Graph update initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

