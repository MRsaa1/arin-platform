"""
ARIN Platform - Risk Analysis Celery Tasks
Фоновые задачи для анализа рисков
"""
import logging
from celery import Task
from typing import Dict, Any

from backend.tasks.celery_app import celery_app
from backend.main import orchestrator, graph_builder_instance

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="backend.tasks.risk_analysis_tasks.analyze_risk_async")
def analyze_risk_async(self: Task, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Асинхронный анализ риска
    
    Args:
        task_data: Данные задачи
        
    Returns:
        Результаты анализа
    """
    try:
        logger.info(f"Processing async risk analysis task: {task_data.get('task_id')}")
        
        # Импорт здесь для избежания циклических зависимостей
        import asyncio
        
        # Создание event loop если нужно
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Выполнение анализа
        if orchestrator:
            result = loop.run_until_complete(
                orchestrator.distribute_task(task_data)
            )
            return result
        else:
            return {"error": "Orchestrator not initialized"}
            
    except Exception as e:
        logger.error(f"Failed to process async risk analysis: {e}")
        raise


@celery_app.task(name="backend.tasks.risk_analysis_tasks.update_graph_periodically")
def update_graph_periodically():
    """Периодическое обновление графа"""
    try:
        logger.info("Updating graph periodically...")
        
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        if graph_builder_instance:
            loop.run_until_complete(graph_builder_instance.save_to_database())
            logger.info("Graph updated successfully")
            return {"status": "success"}
        else:
            return {"status": "skipped", "reason": "Graph Builder not initialized"}
            
    except Exception as e:
        logger.error(f"Failed to update graph: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="backend.tasks.risk_analysis_tasks.cleanup_old_data")
def cleanup_old_data(days: int = 90):
    """
    Очистка старых данных
    
    Args:
        days: Количество дней для хранения данных
    """
    try:
        logger.info(f"Cleaning up data older than {days} days...")
        
        # TODO: Реализовать очистку старых данных из БД
        # - Удаление старых анализов
        # - Архивация старых метрик
        # - Очистка кэша
        
        return {"status": "success", "days": days}
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="backend.tasks.risk_analysis_tasks.batch_risk_analysis")
def batch_risk_analysis(entity_ids: list, task_type: str) -> Dict[str, Any]:
    """
    Пакетный анализ рисков для множества сущностей
    
    Args:
        entity_ids: Список ID сущностей
        task_type: Тип задачи
        
    Returns:
        Результаты пакетного анализа
    """
    try:
        logger.info(f"Processing batch risk analysis for {len(entity_ids)} entities")
        
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        results = {}
        for entity_id in entity_ids:
            task_data = {
                "task_id": f"batch_{entity_id}",
                "type": task_type,
                "entity_id": entity_id,
                "parameters": {}
            }
            
            if orchestrator:
                result = loop.run_until_complete(
                    orchestrator.distribute_task(task_data)
                )
                results[entity_id] = result
        
        return {
            "status": "success",
            "total_processed": len(entity_ids),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Failed to process batch risk analysis: {e}")
        return {"status": "error", "error": str(e)}

