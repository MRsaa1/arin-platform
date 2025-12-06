"""
ARIN Platform - Agents API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel

from backend.main import orchestrator

router = APIRouter()


class AgentStatusResponse(BaseModel):
    """Ответ со статусом агента"""
    agent_id: str
    agent_name: str
    status: str
    metrics: dict


@router.get("", response_model=List[AgentStatusResponse])
async def list_agents():
    """Получить список всех агентов"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    statuses = await orchestrator.get_agent_status()
    
    return [
        AgentStatusResponse(**status)
        for status in statuses.values()
    ]


@router.get("/{agent_id}", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str):
    """Получить статус конкретного агента"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    status = await orchestrator.get_agent_status(agent_id)
    
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    
    return AgentStatusResponse(**status)


@router.post("/{agent_id}/start")
async def start_agent(agent_id: str):
    """Запустить агента"""
    # TODO: Реализовать запуск агента
    return {"message": f"Agent {agent_id} started"}


@router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str):
    """Остановить агента"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    await orchestrator.unregister_agent(agent_id)
    
    return {"message": f"Agent {agent_id} stopped"}

