"""
ARIN Platform - Compliance API
API endpoints для compliance функций
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from backend.compliance.audit_logger import audit_logger, AuditEventType
from backend.compliance.gdpr import gdpr_compliance
from backend.compliance.data_retention import data_retention_manager
from backend.compliance.backup_recovery import backup_manager
from backend.auth.jwt_handler import get_current_user, TokenData
from backend.auth.rbac import require_permission, Permission

router = APIRouter()


# Audit Logs
@router.get("/audit-logs")
async def get_audit_logs(
    user_id: Optional[str] = None,
    event_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=1000),
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Получение audit логов (требует MANAGE_SYSTEM)"""
    events = audit_logger.query_events(
        user_id=user_id,
        event_type=AuditEventType(event_type) if event_type else None,
        resource_type=resource_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return {"events": events, "count": len(events)}


@router.get("/audit-logs/export")
async def export_audit_logs(
    start_date: datetime,
    end_date: datetime,
    format: str = Query("json", regex="^(json|csv)$"),
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Экспорт audit логов"""
    exported = audit_logger.export_audit_logs(start_date, end_date, format)
    return {"format": format, "data": exported}


# GDPR
@router.get("/gdpr/data")
async def get_my_data(
    current_user: TokenData = Depends(get_current_user)
):
    """Получение всех данных пользователя (GDPR Article 15)"""
    user_data = await gdpr_compliance.get_user_data(current_user.user_id or "")
    return user_data


@router.delete("/gdpr/data")
async def delete_my_data(
    current_user: TokenData = Depends(get_current_user)
):
    """Удаление всех данных пользователя (GDPR Article 17)"""
    success = await gdpr_compliance.delete_user_data(current_user.user_id or "")
    if success:
        return {"message": "Data deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete data")


@router.get("/gdpr/export")
async def export_my_data(
    format: str = Query("json", regex="^(json|csv)$"),
    current_user: TokenData = Depends(get_current_user)
):
    """Экспорт данных пользователя (GDPR Article 20)"""
    exported = await gdpr_compliance.export_user_data(
        current_user.user_id or "",
        format
    )
    return {"format": format, "data": exported}


@router.get("/gdpr/privacy-policy")
async def get_privacy_policy():
    """Получение privacy policy"""
    return gdpr_compliance.get_privacy_policy()


# Data Retention
@router.get("/retention/policies")
async def get_retention_policies(
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Получение политик хранения данных"""
    return data_retention_manager.get_retention_summary()


@router.post("/retention/cleanup")
async def cleanup_old_data(
    data_type: Optional[str] = None,
    dry_run: bool = Query(True, description="Only check, don't delete"),
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Очистка старых данных"""
    if data_type:
        result = await data_retention_manager.cleanup_old_data(data_type, dry_run)
    else:
        result = await data_retention_manager.cleanup_all_old_data(dry_run)
    return result


# Backup and Recovery
@router.post("/backup")
async def create_backup(
    backup_type: str = Query("full", regex="^(full|incremental|differential)$"),
    include_data: bool = True,
    include_models: bool = True,
    include_logs: bool = False,
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Создание резервной копии"""
    backup_info = await backup_manager.create_backup(
        backup_type=backup_type,
        include_data=include_data,
        include_models=include_models,
        include_logs=include_logs
    )
    return backup_info


@router.get("/backup")
async def list_backups(
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Список доступных бэкапов"""
    backups = backup_manager.list_backups()
    return {"backups": backups, "count": len(backups)}


@router.post("/backup/{backup_id}/restore")
async def restore_backup(
    backup_id: str,
    components: Optional[List[str]] = None,
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Восстановление из резервной копии"""
    success = await backup_manager.restore_backup(backup_id, components)
    if success:
        return {"message": f"Backup {backup_id} restored successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to restore backup")

