"""
ARIN Platform - Health Check Endpoints
"""
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ARIN Platform"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Детальная проверка здоровья"""
    # TODO: Добавить проверки БД, Redis, Neo4j и т.д.
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ARIN Platform",
        "components": {
            "database": "ok",
            "redis": "ok",
            "neo4j": "ok"
        }
    }

