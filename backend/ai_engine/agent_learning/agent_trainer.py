"""
ARIN Platform - Agent Trainer
Система обучения агентов на исторических данных
"""
import logging
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentTrainer:
    """
    Тренер для обучения агентов на исторических данных
    
    Поддерживает:
    - Обучение на исторических сценариях
    - Адаптацию к новым условиям
    - Continuous learning
    """
    
    def __init__(self):
        """Инициализация Agent Trainer"""
        self.training_history = defaultdict(list)
        self.performance_metrics = defaultdict(dict)
        
    async def train_agent_on_history(
        self,
        agent_id: str,
        historical_data: List[Dict[str, Any]],
        validation_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Обучение агента на исторических данных
        
        Args:
            agent_id: ID агента
            historical_data: Исторические данные (задачи и результаты)
            validation_data: Данные для валидации
            
        Returns:
            Результаты обучения
        """
        try:
            logger.info(f"Training agent {agent_id} on {len(historical_data)} historical samples")
            
            # Анализ исторических данных
            analysis = self._analyze_historical_performance(agent_id, historical_data)
            
            # Извлечение паттернов
            patterns = self._extract_patterns(historical_data)
            
            # Обновление метрик производительности
            self.performance_metrics[agent_id] = {
                "last_training": datetime.now().isoformat(),
                "samples_processed": len(historical_data),
                "patterns_extracted": len(patterns),
                "performance_analysis": analysis
            }
            
            # Сохранение в историю
            training_record = {
                "agent_id": agent_id,
                "timestamp": datetime.now().isoformat(),
                "samples_count": len(historical_data),
                "patterns": patterns,
                "analysis": analysis
            }
            self.training_history[agent_id].append(training_record)
            
            return {
                "status": "success",
                "agent_id": agent_id,
                "samples_processed": len(historical_data),
                "patterns_extracted": len(patterns),
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"Failed to train agent {agent_id}: {e}")
            return {"status": "error", "error": str(e)}
            
    def _analyze_historical_performance(
        self,
        agent_id: str,
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Анализ исторической производительности агента
        
        Args:
            agent_id: ID агента
            historical_data: Исторические данные
            
        Returns:
            Анализ производительности
        """
        if not historical_data:
            return {"error": "No historical data"}
        
        # Извлечение метрик
        success_count = sum(1 for d in historical_data if d.get("status") == "success")
        total_count = len(historical_data)
        success_rate = success_count / total_count if total_count > 0 else 0
        
        # Анализ временных трендов
        timestamps = [
            datetime.fromisoformat(d.get("timestamp", datetime.now().isoformat()))
            for d in historical_data
        ]
        
        # Группировка по периодам
        daily_performance = defaultdict(lambda: {"success": 0, "total": 0})
        for i, data in enumerate(historical_data):
            date = timestamps[i].date()
            daily_performance[date]["total"] += 1
            if data.get("status") == "success":
                daily_performance[date]["success"] += 1
        
        # Расчет тренда
        daily_rates = [
            daily_performance[date]["success"] / daily_performance[date]["total"]
            for date in sorted(daily_performance.keys())
        ]
        
        trend = "improving" if len(daily_rates) > 1 and daily_rates[-1] > daily_rates[0] else "stable"
        
        return {
            "success_rate": float(success_rate),
            "total_samples": total_count,
            "success_count": success_count,
            "trend": trend,
            "daily_performance": {
                str(date): {
                    "success_rate": daily_performance[date]["success"] / daily_performance[date]["total"]
                    if daily_performance[date]["total"] > 0 else 0
                }
                for date in sorted(daily_performance.keys())[-30:]  # Последние 30 дней
            }
        }
        
    def _extract_patterns(
        self,
        historical_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Извлечение паттернов из исторических данных
        
        Args:
            historical_data: Исторические данные
            
        Returns:
            Список паттернов
        """
        patterns = []
        
        # Группировка по типам задач
        task_types = defaultdict(list)
        for data in historical_data:
            task_type = data.get("task_type", "unknown")
            task_types[task_type].append(data)
        
        # Анализ паттернов для каждого типа
        for task_type, tasks in task_types.items():
            success_tasks = [t for t in tasks if t.get("status") == "success"]
            failed_tasks = [t for t in tasks if t.get("status") == "failed"]
            
            if len(success_tasks) > 0:
                patterns.append({
                    "task_type": task_type,
                    "pattern": "successful",
                    "count": len(success_tasks),
                    "common_features": self._extract_common_features(success_tasks)
                })
            
            if len(failed_tasks) > 0:
                patterns.append({
                    "task_type": task_type,
                    "pattern": "failed",
                    "count": len(failed_tasks),
                    "common_features": self._extract_common_features(failed_tasks)
                })
        
        return patterns
        
    def _extract_common_features(
        self,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Извлечение общих признаков из задач
        
        Args:
            tasks: Список задач
            
        Returns:
            Общие признаки
        """
        if not tasks:
            return {}
        
        # Анализ параметров задач
        common_params = {}
        for task in tasks:
            params = task.get("parameters", {})
            for key, value in params.items():
                if key not in common_params:
                    common_params[key] = []
                common_params[key].append(value)
        
        # Вычисление средних/медиан для числовых значений
        features = {}
        for key, values in common_params.items():
            if values and isinstance(values[0], (int, float)):
                features[key] = {
                    "mean": float(np.mean(values)),
                    "median": float(np.median(values)),
                    "std": float(np.std(values))
                }
            else:
                # Для категориальных - наиболее частое значение
                from collections import Counter
                most_common = Counter(values).most_common(1)
                if most_common:
                    features[key] = {"most_common": most_common[0][0]}
        
        return features
        
    async def continuous_learning_update(
        self,
        agent_id: str,
        new_experience: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Обновление агента на основе нового опыта (continuous learning)
        
        Args:
            agent_id: ID агента
            new_experience: Новый опыт (задача и результат)
            
        Returns:
            Результаты обновления
        """
        try:
            # Добавление нового опыта в историю
            self.training_history[agent_id].append({
                "experience": new_experience,
                "timestamp": datetime.now().isoformat()
            })
            
            # Проверка необходимости переобучения
            recent_experiences = [
                exp for exp in self.training_history[agent_id]
                if datetime.fromisoformat(exp["timestamp"]) > datetime.now() - timedelta(days=7)
            ]
            
            if len(recent_experiences) >= 50:  # Порог для переобучения
                logger.info(f"Triggering retraining for {agent_id} based on new experiences")
                # TODO: Вызвать переобучение модели агента
                
            return {
                "status": "success",
                "agent_id": agent_id,
                "experience_added": True,
                "total_experiences": len(self.training_history[agent_id])
            }
            
        except Exception as e:
            logger.error(f"Failed to update agent {agent_id} with new experience: {e}")
            return {"status": "error", "error": str(e)}
            
    def get_agent_performance(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Получение метрик производительности агента
        
        Args:
            agent_id: ID агента
            
        Returns:
            Метрики производительности
        """
        return self.performance_metrics.get(agent_id, {})
        
    def get_training_history(
        self,
        agent_id: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Получение истории обучения
        
        Args:
            agent_id: ID агента (если None, все агенты)
            
        Returns:
            История обучения
        """
        if agent_id:
            return {agent_id: self.training_history.get(agent_id, [])}
        return dict(self.training_history)

