"""
ARIN Platform - Credit Risk ML Model
ML модель для предсказания дефолта
"""
import logging
import pickle
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available, using placeholder model")

logger = logging.getLogger(__name__)


class CreditRiskModel:
    """
    ML модель для предсказания вероятности дефолта
    
    Использует XGBoost для классификации
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Инициализация модели
        
        Args:
            model_path: Путь к сохраненной модели
        """
        self.model = None
        self.model_path = model_path
        self.feature_names = [
            'debt_to_equity',
            'ebitda_margin',
            'current_ratio',
            'revenue_normalized',
            'debt_normalized',
            'news_count',
            # Можно добавить больше признаков
        ]
        
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None
    ) -> Dict[str, Any]:
        """
        Обучение модели
        
        Args:
            X_train: Признаки для обучения
            y_train: Целевая переменная (0 - нет дефолта, 1 - дефолт)
            X_val: Признаки для валидации (опционально)
            y_val: Целевая переменная для валидации (опционально)
            
        Returns:
            Метрики обучения
        """
        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available, cannot train model")
            return {"error": "XGBoost not available"}
            
        try:
            # Создание модели XGBoost с улучшенными параметрами
            self.model = xgb.XGBClassifier(
                n_estimators=200,  # Увеличено для лучшей точности
                max_depth=6,  # Увеличена глубина
                learning_rate=0.05,  # Снижен learning rate для более стабильного обучения
                subsample=0.8,  # Subsampling для предотвращения переобучения
                colsample_bytree=0.8,  # Feature subsampling
                min_child_weight=3,  # Минимальный вес для листа
                gamma=0.1,  # Минимальное снижение потерь для разделения
                random_state=42,
                eval_metric='logloss',
                early_stopping_rounds=20  # Early stopping для предотвращения переобучения
            )
            
            # Обучение
            if X_val is not None and y_val is not None:
                self.model.fit(
                    X_train,
                    y_train,
                    eval_set=[(X_val, y_val)],
                    verbose=False
                )
            else:
                self.model.fit(X_train, y_train)
                
            # Оценка качества
            train_score = self.model.score(X_train, y_train)
            metrics = {
                "train_accuracy": float(train_score),
                "model_type": "XGBoost"
            }
            
            if X_val is not None and y_val is not None:
                val_score = self.model.score(X_val, y_val)
                metrics["val_accuracy"] = float(val_score)
                
            logger.info(f"Model trained successfully. Train accuracy: {train_score:.4f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            raise
            
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Предсказание вероятности дефолта
        
        Args:
            X: Признаки для предсказания
            
        Returns:
            Вероятности [P(no default), P(default)]
        """
        if self.model is None:
            # Возвращаем базовое предсказание если модель не обучена
            logger.warning("Model not trained, returning default prediction")
            n_samples = X.shape[0] if hasattr(X, 'shape') else len(X)
            return np.array([[0.95, 0.05]] * n_samples)
            
        try:
            return self.model.predict_proba(X)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # Fallback к базовому предсказанию
            n_samples = X.shape[0] if hasattr(X, 'shape') else len(X)
            return np.array([[0.95, 0.05]] * n_samples)
            
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Предсказание класса (0 или 1)
        
        Args:
            X: Признаки для предсказания
            
        Returns:
            Предсказанные классы
        """
        if self.model is None:
            return np.array([0] * (X.shape[0] if hasattr(X, 'shape') else len(X)))
            
        try:
            return self.model.predict(X)
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return np.array([0] * (X.shape[0] if hasattr(X, 'shape') else len(X)))
            
    def save(self, filepath: str):
        """
        Сохранение модели
        
        Args:
            filepath: Путь для сохранения
        """
        if self.model is None:
            logger.warning("No model to save")
            return
            
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'feature_names': self.feature_names
                }, f)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            raise
            
    def load(self, filepath: str):
        """
        Загрузка модели
        
        Args:
            filepath: Путь к модели
        """
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.feature_names = data.get('feature_names', self.feature_names)
            logger.info(f"Model loaded from {filepath}")
        except FileNotFoundError:
            logger.warning(f"Model file not found: {filepath}")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Получение важности признаков
        
        Returns:
            Словарь с важностью признаков
        """
        if self.model is None or not XGBOOST_AVAILABLE:
            return None
            
        try:
            importance = self.model.feature_importances_
            return dict(zip(self.feature_names, importance.tolist()))
        except Exception as e:
            logger.error(f"Failed to get feature importance: {e}")
            return None


def create_sample_training_data(n_samples: int = 1000) -> tuple:
    """
    Создание примерных данных для обучения (для тестирования)
    
    Args:
        n_samples: Количество образцов
        
    Returns:
        (X, y) - признаки и целевая переменная
    """
    np.random.seed(42)
    
    # Генерация признаков
    X = pd.DataFrame({
        'debt_to_equity': np.random.uniform(0.1, 2.0, n_samples),
        'ebitda_margin': np.random.uniform(0.05, 0.4, n_samples),
        'current_ratio': np.random.uniform(0.5, 3.0, n_samples),
        'revenue_normalized': np.random.uniform(0.1, 10.0, n_samples),
        'debt_normalized': np.random.uniform(0.1, 5.0, n_samples),
        'news_count': np.random.poisson(5, n_samples)
    })
    
    # Генерация целевой переменной на основе признаков
    # Высокий debt_to_equity и низкий ebitda_margin увеличивают вероятность дефолта
    default_prob = (
        0.1 * (X['debt_to_equity'] / 2.0) +
        0.2 * (1 - X['ebitda_margin'] / 0.4) +
        0.1 * (1 - X['current_ratio'] / 3.0) +
        np.random.normal(0, 0.1, n_samples)
    )
    default_prob = np.clip(default_prob, 0, 1)
    
    y = (default_prob > 0.3).astype(int)  # Дефолт если вероятность >30%
    
    return X, y

