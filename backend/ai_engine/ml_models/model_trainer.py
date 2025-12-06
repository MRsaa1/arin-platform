"""
ARIN Platform - Model Trainer
Система автоматического переобучения моделей
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

from backend.ai_engine.ml_models.model_evaluator import ModelEvaluator
from backend.ai_engine.ml_models.credit_risk_model import CreditRiskModel

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Тренер моделей с поддержкой автоматического переобучения
    """
    
    def __init__(self, models_dir: str = "backend/models"):
        """
        Инициализация Model Trainer
        
        Args:
            models_dir: Директория для сохранения моделей
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.evaluator = ModelEvaluator()
        self.training_history = []
        
    async def train_credit_risk_model(
        self,
        training_data: pd.DataFrame,
        target_column: str = "default",
        test_size: float = 0.2,
        retrain: bool = False
    ) -> Dict[str, Any]:
        """
        Обучение Credit Risk модели
        
        Args:
            training_data: Данные для обучения
            target_column: Название целевой колонки
            test_size: Доля тестовых данных
            retrain: Переобучить существующую модель
            
        Returns:
            Результаты обучения
        """
        try:
            from sklearn.model_selection import train_test_split
            
            # Подготовка данных
            if target_column not in training_data.columns:
                raise ValueError(f"Target column '{target_column}' not found in data")
            
            X = training_data.drop(columns=[target_column])
            y = training_data[target_column]
            
            # Разделение на train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            
            # Создание и обучение модели
            model = CreditRiskModel()
            
            # Обучение с валидацией
            train_metrics = model.train(X_train, y_train, X_test, y_test)
            
            # Оценка на тестовых данных
            y_pred = model.predict(X_test.values)
            y_proba = model.predict_proba(X_test.values)
            
            test_metrics = self.evaluator.evaluate_classification(
                y_test.values,
                y_pred,
                y_proba,
                model_name="credit_risk_model"
            )
            
            # Проверка дрифта если есть базовая модель
            drift_result = None
            if not retrain:
                baseline_model_path = self.models_dir / "credit_risk_model.pkl"
                if baseline_model_path.exists():
                    baseline_model = CreditRiskModel()
                    baseline_model.load(str(baseline_model_path))
                    baseline_pred = baseline_model.predict(X_test.values)
                    baseline_proba = baseline_model.predict_proba(X_test.values)
                    baseline_metrics = self.evaluator.evaluate_classification(
                        y_test.values,
                        baseline_pred,
                        baseline_proba,
                        model_name="credit_risk_model_baseline"
                    )
                    drift_result = self.evaluator.detect_model_drift(
                        test_metrics,
                        baseline_metrics
                    )
            
            # Сохранение модели
            model_path = self.models_dir / "credit_risk_model.pkl"
            model.save(str(model_path))
            
            # Сохранение метрик
            training_record = {
                "model_name": "credit_risk_model",
                "timestamp": datetime.now().isoformat(),
                "train_metrics": train_metrics,
                "test_metrics": test_metrics,
                "drift_detected": drift_result["drift_detected"] if drift_result else False,
                "model_path": str(model_path)
            }
            self.training_history.append(training_record)
            
            result = {
                "status": "success",
                "model_name": "credit_risk_model",
                "train_metrics": train_metrics,
                "test_metrics": test_metrics,
                "model_path": str(model_path),
                "feature_importance": model.get_feature_importance()
            }
            
            if drift_result:
                result["drift_analysis"] = drift_result
            
            logger.info(f"Credit Risk model trained successfully. Test accuracy: {test_metrics.get('accuracy', 0):.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to train credit risk model: {e}")
            return {"status": "error", "error": str(e)}
            
    async def auto_retrain_if_needed(
        self,
        model_name: str,
        new_data: pd.DataFrame,
        min_samples: int = 100,
        performance_threshold: float = 0.05
    ) -> Dict[str, Any]:
        """
        Автоматическое переобучение если необходимо
        
        Args:
            model_name: Имя модели
            new_data: Новые данные
            min_samples: Минимальное количество новых образцов для переобучения
            performance_threshold: Порог снижения производительности для переобучения
            
        Returns:
            Результаты переобучения
        """
        if len(new_data) < min_samples:
            return {
                "status": "skipped",
                "reason": f"Insufficient new data: {len(new_data)} < {min_samples}"
            }
        
        # Проверка производительности текущей модели
        model_path = self.models_dir / f"{model_name}.pkl"
        if not model_path.exists():
            return {
                "status": "skipped",
                "reason": "No existing model found"
            }
        
        # Загрузка текущей модели
        if model_name == "credit_risk_model":
            current_model = CreditRiskModel()
            current_model.load(str(model_path))
            
            # Оценка на новых данных (если есть метки)
            # TODO: В production нужны метки для новых данных
            # Пока что просто переобучаем если достаточно данных
            
            # Переобучение
            return await self.train_credit_risk_model(
                training_data=new_data,
                retrain=True
            )
        
        return {
            "status": "skipped",
            "reason": f"Auto-retrain not implemented for {model_name}"
        }
        
    def get_training_history(
        self,
        model_name: Optional[str] = None,
        days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Получение истории обучения
        
        Args:
            model_name: Имя модели
            days: Количество дней
            
        Returns:
            История обучения
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        history = [
            record for record in self.training_history
            if datetime.fromisoformat(record["timestamp"]) >= cutoff_date
        ]
        
        if model_name:
            history = [r for r in history if r.get("model_name") == model_name]
        
        return history

