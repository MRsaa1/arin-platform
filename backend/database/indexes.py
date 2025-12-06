"""
ARIN Platform - Database Indexes
Определение индексов для оптимизации запросов
"""
import logging
from sqlalchemy import Index, text
from typing import List

logger = logging.getLogger(__name__)


# Список индексов для создания
INDEXES = [
    # Индексы для таблицы risk_analyses
    Index('idx_risk_analyses_entity_id', 'entity_id'),
    Index('idx_risk_analyses_agent_id', 'agent_id'),
    Index('idx_risk_analyses_timestamp', 'timestamp'),
    Index('idx_risk_analyses_entity_agent', 'entity_id', 'agent_id'),
    Index('idx_risk_analyses_timestamp_entity', 'timestamp', 'entity_id'),
    
    # Индексы для таблицы graph_nodes
    Index('idx_graph_nodes_node_type', 'node_type'),
    Index('idx_graph_nodes_risk_score', 'risk_score'),
    Index('idx_graph_nodes_type_risk', 'node_type', 'risk_score'),
    
    # Индексы для таблицы graph_edges
    Index('idx_graph_edges_source', 'source_id'),
    Index('idx_graph_edges_target', 'target_id'),
    Index('idx_graph_edges_relationship', 'relationship_type'),
    Index('idx_graph_edges_source_target', 'source_id', 'target_id'),
    
    # Индексы для таблицы agent_tasks
    Index('idx_agent_tasks_agent_id', 'agent_id'),
    Index('idx_agent_tasks_status', 'status'),
    Index('idx_agent_tasks_timestamp', 'created_at'),
    Index('idx_agent_tasks_agent_status', 'agent_id', 'status'),
    
    # Индексы для таблицы alerts
    Index('idx_alerts_severity', 'severity'),
    Index('idx_alerts_status', 'status'),
    Index('idx_alerts_timestamp', 'created_at'),
    Index('idx_alerts_severity_status', 'severity', 'status'),
]


async def create_indexes(engine):
    """
    Создание индексов в БД
    
    Args:
        engine: SQLAlchemy engine
    """
    async with engine.begin() as conn:
        for index in INDEXES:
            try:
                await conn.execute(text(str(index.compile(engine))))
                logger.info(f"Created index: {index.name}")
            except Exception as e:
                logger.warning(f"Failed to create index {index.name}: {e}")


async def analyze_query_performance(engine, query: str) -> dict:
    """
    Анализ производительности запроса
    
    Args:
        engine: SQLAlchemy engine
        query: SQL запрос
        
    Returns:
        Результаты анализа (EXPLAIN ANALYZE)
    """
    async with engine.begin() as conn:
        explain_query = f"EXPLAIN ANALYZE {query}"
        result = await conn.execute(text(explain_query))
        rows = result.fetchall()
        
        return {
            "query": query,
            "explain": "\n".join(str(row) for row in rows)
        }

