"""
ARIN Platform - ML Models Management API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd

from backend.ai_engine.ml_models.model_trainer import ModelTrainer
from backend.ai_engine.ml_models.model_evaluator import ModelEvaluator
from backend.ai_engine.agent_learning.agent_trainer import AgentTrainer

router = APIRouter()

# Глобальные экземпляры
model_trainer = ModelTrainer()
model_evaluator = ModelEvaluator()
agent_trainer = AgentTrainer()


class TrainModelRequest(BaseModel):
    """Запрос на обучение модели"""
    model_name: str
    test_size: float = 0.2
    retrain: bool = False


class EvaluateModelRequest(BaseModel):
    """Запрос на оценку модели"""
    model_name: str
    y_true: List[float]
    y_pred: List[float]
    y_proba: Optional[List[List[float]]] = None


@router.post("/train")
async def train_model(request: TrainModelRequest, file: UploadFile = File(...)):
    """Обучить модель"""
    try:
        # Чтение данных из файла
        contents = await file.read()
        df = pd.read_csv(contents.decode('utf-8'))
        
        if request.model_name == "credit_risk_model":
            result = await model_trainer.train_credit_risk_model(
                training_data=df,
                test_size=request.test_size,
                retrain=request.retrain
            )
            return result
        else:
            raise HTTPException(status_code=400, detail=f"Unknown model: {request.model_name}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate")
async def evaluate_model(request: EvaluateModelRequest):
    """Оценить модель"""
    try:
        import numpy as np
        
        y_true = np.array(request.y_true)
        y_pred = np.array(request.y_pred)
        y_proba = np.array(request.y_proba) if request.y_proba else None
        
        metrics = model_evaluator.evaluate_classification(
            y_true=y_true,
            y_pred=y_pred,
            y_proba=y_proba,
            model_name=request.model_name
        )
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training-history")
async def get_training_history(model_name: Optional[str] = None, days: int = 90):
    """Получить историю обучения"""
    try:
        history = model_trainer.get_training_history(
            model_name=model_name,
            days=days
        )
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/train")
async def train_agent(agent_id: str, historical_data: List[dict]):
    """Обучить агента на исторических данных"""
    try:
        result = await agent_trainer.train_agent_on_history(
            agent_id=agent_id,
            historical_data=historical_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/performance")
async def get_agent_performance(agent_id: str):
    """Получить метрики производительности агента"""
    try:
        performance = agent_trainer.get_agent_performance(agent_id)
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/learn")
async def continuous_learning(agent_id: str, experience: dict):
    """Continuous learning для агента"""
    try:
        result = await agent_trainer.continuous_learning_update(
            agent_id=agent_id,
            new_experience=experience
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

