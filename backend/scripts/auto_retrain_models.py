"""
ARIN Platform - Automatic Model Retraining Script
Автоматическое переобучение моделей на основе новых данных и дрифта
"""
import asyncio
import logging
from pathlib import Path
import sys

# Добавление пути к backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ai_engine.ml_models.model_trainer import ModelTrainer
from backend.ai_engine.ml_models.model_evaluator import ModelEvaluator
from backend.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция для автоматического переобучения"""
    logger.info("Starting automatic model retraining...")
    
    trainer = ModelTrainer()
    evaluator = ModelEvaluator()
    
    # TODO: Получение новых данных из БД
    # В production это будет запрос к БД для получения новых данных
    # new_data = await get_new_training_data()
    
    # Пример: проверка необходимости переобучения
    # Для демонстрации используем примерные данные
    from backend.ai_engine.ml_models.credit_risk_model import create_sample_training_data
    
    logger.info("Generating sample training data...")
    X, y = create_sample_training_data(n_samples=500)
    training_data = X.copy()
    training_data['default'] = y
    
    # Обучение модели
    logger.info("Training credit risk model...")
    result = await trainer.train_credit_risk_model(
        training_data=training_data,
        test_size=0.2,
        retrain=False
    )
    
    if result.get("status") == "success":
        logger.info(f"Model trained successfully: {result.get('test_metrics', {})}")
        
        # Проверка дрифта
        if "drift_analysis" in result:
            drift = result["drift_analysis"]
            if drift.get("drift_detected"):
                logger.warning(f"Model drift detected: {drift}")
            else:
                logger.info("No model drift detected")
    else:
        logger.error(f"Model training failed: {result.get('error')}")
    
    logger.info("Automatic model retraining completed")


if __name__ == "__main__":
    asyncio.run(main())

