"""
ARIN Platform - Compliance Celery Tasks
Периодические задачи для compliance
"""
import logging
from datetime import datetime

from backend.tasks.celery_app import celery_app
from backend.compliance.data_retention import data_retention_manager
from backend.compliance.backup_recovery import backup_manager

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.tasks.compliance_tasks.cleanup_old_data")
def cleanup_old_data_task():
    """Периодическая очистка старых данных"""
    try:
        logger.info("Starting scheduled data cleanup...")
        result = data_retention_manager.cleanup_all_old_data(dry_run=False)
        logger.info(f"Data cleanup completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Data cleanup failed: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="backend.tasks.compliance_tasks.create_scheduled_backup")
def create_scheduled_backup():
    """Создание запланированного бэкапа"""
    try:
        logger.info("Creating scheduled backup...")
        backup_info = backup_manager.create_backup(
            backup_type="full",
            include_data=True,
            include_models=True,
            include_logs=False
        )
        logger.info(f"Backup created: {backup_info['backup_id']}")
        return backup_info
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="backend.tasks.compliance_tasks.cleanup_old_backups")
def cleanup_old_backups(keep_days: int = 30):
    """Очистка старых бэкапов"""
    try:
        logger.info(f"Cleaning up backups older than {keep_days} days...")
        deleted_count = backup_manager.cleanup_old_backups(keep_days)
        logger.info(f"Deleted {deleted_count} old backups")
        return {"deleted_count": deleted_count}
    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}")
        return {"status": "error", "error": str(e)}

