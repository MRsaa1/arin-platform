"""
ARIN Platform - Model Evaluator
Система оценки и мониторинга ML моделей
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """
    Оценщик моделей для мониторинга качества и дрифта
    """
    
    def __init__(self):
        """Инициализация Model Evaluator"""
        self.evaluation_history = []
        
    def evaluate_classification(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_proba: Optional[np.ndarray] = None,
        model_name: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Оценка классификационной модели
        
        Args:
            y_true: Истинные метки
            y_pred: Предсказанные метки
            y_proba: Вероятности (для ROC-AUC)
            model_name: Имя модели
            
        Returns:
            Метрики оценки
        """
        try:
            metrics = {
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "accuracy": float(accuracy_score(y_true, y_pred)),
                "precision": float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
                "recall": float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
                "f1_score": float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
                "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
            }
            
            # ROC-AUC если есть вероятности
            if y_proba is not None:
                try:
                    if y_proba.ndim > 1 and y_proba.shape[1] > 1:
                        # Многоклассовая классификация
                        metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba, multi_class='ovr', average='weighted'))
                    else:
                        # Бинарная классификация
                        y_proba_binary = y_proba[:, 1] if y_proba.ndim > 1 else y_proba
                        metrics["roc_auc"] = float(roc_auc_score(y_true, y_proba_binary))
                except Exception as e:
                    logger.warning(f"Failed to calculate ROC-AUC: {e}")
            
            # Classification report
            try:
                report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
                metrics["classification_report"] = report
            except Exception as e:
                logger.warning(f"Failed to generate classification report: {e}")
            
            # Сохранение в историю
            self.evaluation_history.append(metrics)
            
            logger.info(
                f"Model {model_name} evaluated: "
                f"Accuracy={metrics['accuracy']:.4f}, "
                f"F1={metrics['f1_score']:.4f}"
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            return {"error": str(e)}
            
    def evaluate_regression(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        model_name: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Оценка регрессионной модели
        
        Args:
            y_true: Истинные значения
            y_pred: Предсказанные значения
            model_name: Имя модели
            
        Returns:
            Метрики оценки
        """
        try:
            from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
            
            mse = mean_squared_error(y_true, y_pred)
            mae = mean_absolute_error(y_true, y_pred)
            r2 = r2_score(y_true, y_pred)
            rmse = np.sqrt(mse)
            
            metrics = {
                "model_name": model_name,
                "timestamp": datetime.now().isoformat(),
                "mse": float(mse),
                "mae": float(mae),
                "rmse": float(rmse),
                "r2_score": float(r2),
                "mean_absolute_percentage_error": float(np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100)
            }
            
            # Сохранение в историю
            self.evaluation_history.append(metrics)
            
            logger.info(
                f"Model {model_name} evaluated: "
                f"RMSE={metrics['rmse']:.4f}, "
                f"R2={metrics['r2_score']:.4f}"
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to evaluate model: {e}")
            return {"error": str(e)}
            
    def detect_model_drift(
        self,
        current_metrics: Dict[str, Any],
        baseline_metrics: Dict[str, Any],
        threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Обнаружение дрифта модели
        
        Args:
            current_metrics: Текущие метрики
            baseline_metrics: Базовые метрики
            threshold: Порог для обнаружения дрифта (10% по умолчанию)
            
        Returns:
            Результаты обнаружения дрифта
        """
        drift_detected = False
        drift_details = {}
        
        # Сравнение ключевых метрик
        key_metrics = ["accuracy", "f1_score", "roc_auc", "rmse", "r2_score"]
        
        for metric in key_metrics:
            if metric in current_metrics and metric in baseline_metrics:
                current_value = current_metrics[metric]
                baseline_value = baseline_metrics[metric]
                
                if baseline_value != 0:
                    change_percent = abs((current_value - baseline_value) / baseline_value)
                    
                    if change_percent > threshold:
                        drift_detected = True
                        drift_details[metric] = {
                            "baseline": baseline_value,
                            "current": current_value,
                            "change_percent": change_percent * 100,
                            "drift_detected": True
                        }
                    else:
                        drift_details[metric] = {
                            "baseline": baseline_value,
                            "current": current_value,
                            "change_percent": change_percent * 100,
                            "drift_detected": False
                        }
        
        return {
            "drift_detected": drift_detected,
            "threshold": threshold,
            "details": drift_details,
            "recommendation": "Retrain model" if drift_detected else "Model performance stable"
        }
        
    def compare_models(
        self,
        model_metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Сравнение нескольких моделей
        
        Args:
            model_metrics: Список метрик моделей
            
        Returns:
            Результаты сравнения
        """
        if not model_metrics:
            return {"error": "No models to compare"}
        
        comparison = {
            "models": model_metrics,
            "best_model": None,
            "ranking": []
        }
        
        # Определение лучшей модели по F1 score или R2 score
        best_score = -1
        best_model = None
        
        for metrics in model_metrics:
            score = None
            if "f1_score" in metrics:
                score = metrics["f1_score"]
            elif "r2_score" in metrics:
                score = metrics["r2_score"]
            elif "accuracy" in metrics:
                score = metrics["accuracy"]
            
            if score is not None and score > best_score:
                best_score = score
                best_model = metrics["model_name"]
        
        comparison["best_model"] = best_model
        
        # Ранжирование моделей
        scores = []
        for metrics in model_metrics:
            score = None
            if "f1_score" in metrics:
                score = metrics["f1_score"]
            elif "r2_score" in metrics:
                score = metrics["r2_score"]
            elif "accuracy" in metrics:
                score = metrics["accuracy"]
            
            if score is not None:
                scores.append((metrics["model_name"], score))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        comparison["ranking"] = [{"model": name, "score": score} for name, score in scores]
        
        return comparison
        
    def get_evaluation_history(
        self,
        model_name: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Получение истории оценок
        
        Args:
            model_name: Имя модели (если None, все модели)
            days: Количество дней для фильтрации
            
        Returns:
            История оценок
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        history = [
            eval_data for eval_data in self.evaluation_history
            if datetime.fromisoformat(eval_data["timestamp"]) >= cutoff_date
        ]
        
        if model_name:
            history = [e for e in history if e.get("model_name") == model_name]
        
        return history

