"""
ARIN Platform - Celery Tasks API
Управление асинхронными задачами
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from celery.result import AsyncResult

from backend.tasks.celery_app import celery_app

router = APIRouter()


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """Получить статус задачи Celery"""
    try:
        task_result = AsyncResult(task_id, app=celery_app)
        
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None,
            "error": str(task_result.info) if task_result.failed() else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Отменить задачу Celery"""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"message": f"Task {task_id} cancelled", "task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

