"""
ARIN Platform - Risk Analysis API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

from backend.main import orchestrator

router = APIRouter()


class RiskAnalysisRequest(BaseModel):
    """Запрос на анализ риска"""
    type: str
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    required_agents: Optional[list] = None
    parameters: Optional[dict] = None


class RiskAnalysisResponse(BaseModel):
    """Ответ с результатами анализа"""
    task_id: str
    timestamp: str
    status: str
    results: dict


@router.post("/analyze", response_model=RiskAnalysisResponse)
async def analyze_risk(
    request: RiskAnalysisRequest,
    async_mode: bool = Query(False, description="Execute asynchronously via Celery")
):
    """
    Запустить анализ риска
    
    Выполняет анализ риска для указанной сущности с использованием соответствующих агентов.
    
    **Типы анализа**:
    - `credit_analysis`: Кредитный риск
    - `market_analysis`: Рыночный риск
    - `operational_analysis`: Операционный риск
    - `liquidity_analysis`: Риск ликвидности
    - `regulatory_analysis`: Регуляторный риск
    - `systemic_analysis`: Системный риск
    - `comprehensive_analysis`: Комплексный анализ всех типов
    
    **Асинхронный режим**:
    - Если `async_mode=true`, анализ выполняется через Celery
    - Возвращает `task_id` для отслеживания статуса
    - Используйте `GET /api/v1/tasks/{task_id}` для проверки статуса
    
    **Примеры**:
    
    Кредитный анализ:
    ```json
    {
      "type": "credit_analysis",
      "entity_id": "AAPL",
      "entity_type": "company",
      "parameters": {
        "include_news": true,
        "include_financials": true
      }
    }
    ```
    
    Комплексный анализ:
    ```json
    {
      "type": "comprehensive_analysis",
      "entity_id": "MSFT",
      "entity_type": "company"
    }
    ```
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    task = {
        "task_id": str(uuid.uuid4()),
        "type": request.type,
        "entity_id": request.entity_id,
        "entity_type": request.entity_type,
        "required_agents": request.required_agents,
        "parameters": request.parameters or {},
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        if async_mode:
            # Асинхронное выполнение через Celery
            from backend.tasks.risk_analysis_tasks import analyze_risk_async
            celery_task = analyze_risk_async.delay(task)
            
            return RiskAnalysisResponse(
                task_id=task["task_id"],
                timestamp=datetime.now().isoformat(),
                status="processing",
                results={
                    "celery_task_id": celery_task.id,
                    "message": "Task submitted for async processing"
                }
            )
        else:
            # Синхронное выполнение
            result = await orchestrator.distribute_task(task)
            
            return RiskAnalysisResponse(
                task_id=task["task_id"],
                timestamp=result["timestamp"],
                status=result["overall_status"],
                results=result
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
async def get_current_risks():
    """Получить текущие риски"""
    # TODO: Реализовать получение текущих рисков
    return {"risks": []}


@router.get("/history")
async def get_risk_history():
    """Получить историю рисков"""
    # TODO: Реализовать получение истории
    return {"history": []}

