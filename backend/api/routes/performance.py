"""
ARIN Platform - Performance Monitoring API
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.services.performance_monitor import performance_monitor
from backend.services.cache_service import cache_service

router = APIRouter()


@router.get("/health")
async def get_system_health():
    """Получить общее здоровье системы"""
    try:
        health = performance_monitor.get_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requests")
async def get_request_statistics(
    request_type: Optional[str] = Query(None, description="Type of request"),
    hours: int = Query(24, description="Hours to analyze")
):
    """Получить статистику запросов"""
    try:
        stats = performance_monitor.get_request_statistics(
            request_type=request_type,
            hours=hours
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_agent_performance(agent_id: Optional[str] = None):
    """Получить производительность агентов"""
    try:
        performance = performance_monitor.get_agent_performance(agent_id=agent_id)
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_statistics():
    """Получить статистику кэша"""
    try:
        stats = await cache_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cache/clear")
async def clear_cache():
    """Очистить кэш"""
    try:
        result = await cache_service.clear_all()
        return {"success": result, "message": "Cache cleared" if result else "Cache clear failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

