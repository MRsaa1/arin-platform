"""
ARIN Platform - Celery Application
Асинхронная обработка фоновых задач
"""
import logging
from celery import Celery
from celery.schedules import crontab

from backend.config import settings

logger = logging.getLogger(__name__)

# Создание Celery приложения
celery_app = Celery(
    "arin_platform",
    broker=settings.redis_url,  # Redis как message broker
    backend=settings.redis_url,  # Redis как result backend
    include=["backend.tasks.risk_analysis_tasks", "backend.tasks.model_training_tasks"]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Периодические задачи
celery_app.conf.beat_schedule = {
    "update-graph-periodically": {
        "task": "backend.tasks.risk_analysis_tasks.update_graph_periodically",
        "schedule": crontab(minute="*/5"),  # Каждые 5 минут
    },
    "retrain-models-if-needed": {
        "task": "backend.tasks.model_training_tasks.auto_retrain_models",
        "schedule": crontab(hour=2, minute=0),  # Каждый день в 2:00
    },
    "cleanup-old-data": {
        "task": "backend.tasks.risk_analysis_tasks.cleanup_old_data",
        "schedule": crontab(hour=3, minute=0),  # Каждый день в 3:00
    },
}

