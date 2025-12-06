"""
ARIN Platform - Script для обучения Credit Risk ML модели
"""
import asyncio
import sys
from pathlib import Path

# Добавление пути к backend
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ai_engine.ml_models.credit_risk_model import (
    CreditRiskModel,
    create_sample_training_data
)
import pandas as pd
from sklearn.model_selection import train_test_split
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция для обучения модели"""
    logger.info("Starting Credit Risk Model training...")
    
    # Создание данных для обучения
    logger.info("Generating training data...")
    X, y = create_sample_training_data(n_samples=2000)
    
    # Разделение на train/val
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Validation set: {len(X_val)} samples")
    logger.info(f"Default rate: {y.mean():.2%}")
    
    # Создание и обучение модели
    model = CreditRiskModel()
    
    logger.info("Training model...")
    metrics = model.train(X_train, y_train, X_val, y_val)
    
    logger.info(f"Training metrics: {metrics}")
    
    # Сохранение модели
    model_path = Path(__file__).parent.parent / "models" / "credit_risk_model.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    
    model.save(str(model_path))
    logger.info(f"Model saved to {model_path}")
    
    # Вывод важности признаков
    feature_importance = model.get_feature_importance()
    if feature_importance:
        logger.info("Feature importance:")
        for feature, importance in sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            logger.info(f"  {feature}: {importance:.4f}")
    
    logger.info("Training completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

