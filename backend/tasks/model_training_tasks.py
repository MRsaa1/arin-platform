"""
ARIN Platform - Model Training Celery Tasks
Фоновые задачи для обучения моделей
"""
import logging
from typing import Dict, Any

from backend.tasks.celery_app import celery_app
from backend.ai_engine.ml_models.model_trainer import ModelTrainer

logger = logging.getLogger(__name__)


@celery_app.task(name="backend.tasks.model_training_tasks.auto_retrain_models")
def auto_retrain_models():
    """Автоматическое переобучение моделей"""
    try:
        logger.info("Starting automatic model retraining...")
        
        import asyncio
        from backend.ai_engine.ml_models.credit_risk_model import create_sample_training_data
        import pandas as pd
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        trainer = ModelTrainer()
        
        # Получение новых данных (в production из БД)
        X, y = create_sample_training_data(n_samples=500)
        training_data = X.copy()
        training_data['default'] = y
        
        # Переобучение
        result = loop.run_until_complete(
            trainer.train_credit_risk_model(
                training_data=training_data,
                retrain=True
            )
        )
        
        logger.info(f"Model retraining completed: {result.get('status')}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to retrain models: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="backend.tasks.model_training_tasks.train_model_async")
def train_model_async(model_name: str, training_data_path: str) -> Dict[str, Any]:
    """
    Асинхронное обучение модели
    
    Args:
        model_name: Имя модели
        training_data_path: Путь к данным для обучения
        
    Returns:
        Результаты обучения
    """
    try:
        logger.info(f"Training {model_name} model asynchronously...")
        
        import asyncio
        import pandas as pd
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Загрузка данных
        training_data = pd.read_csv(training_data_path)
        
        trainer = ModelTrainer()
        
        if model_name == "credit_risk_model":
            result = loop.run_until_complete(
                trainer.train_credit_risk_model(training_data=training_data)
            )
            return result
        else:
            return {"status": "error", "error": f"Unknown model: {model_name}"}
            
    except Exception as e:
        logger.error(f"Failed to train model asynchronously: {e}")
        return {"status": "error", "error": str(e)}

