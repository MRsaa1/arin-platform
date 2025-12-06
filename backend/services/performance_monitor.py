"""
ARIN Platform - Performance Monitor
Мониторинг производительности системы
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import time
import asyncio

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Мониторинг производительности системы
    
    Отслеживает:
    - Время выполнения запросов
    - Использование ресурсов
    - Производительность агентов
    - Производительность БД
    """
    
    def __init__(self):
        """Инициализация Performance Monitor"""
        self.metrics = defaultdict(list)
        self.active_requests = {}
        self.agent_performance = defaultdict(dict)
        
    def start_request(self, request_id: str, request_type: str):
        """Начало отслеживания запроса"""
        self.active_requests[request_id] = {
            "type": request_type,
            "start_time": time.time(),
            "timestamp": datetime.now()
        }
        
    def end_request(self, request_id: str, status: str = "success"):
        """Завершение отслеживания запроса"""
        if request_id not in self.active_requests:
            return
            
        request_info = self.active_requests.pop(request_id)
        duration = time.time() - request_info["start_time"]
        
        metric = {
            "request_id": request_id,
            "type": request_info["type"],
            "duration": duration,
            "status": status,
            "timestamp": request_info["timestamp"].isoformat()
        }
        
        self.metrics[request_info["type"]].append(metric)
        
        # Ограничение истории (последние 1000 запросов каждого типа)
        if len(self.metrics[request_info["type"]]) > 1000:
            self.metrics[request_info["type"]] = self.metrics[request_info["type"]][-1000:]
            
    def record_agent_performance(
        self,
        agent_id: str,
        task_id: str,
        duration: float,
        status: str = "success"
    ):
        """Запись производительности агента"""
        if agent_id not in self.agent_performance:
            self.agent_performance[agent_id] = {
                "tasks": [],
                "total_tasks": 0,
                "successful_tasks": 0,
                "failed_tasks": 0,
                "average_duration": 0.0
            }
        
        perf = self.agent_performance[agent_id]
        perf["tasks"].append({
            "task_id": task_id,
            "duration": duration,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        
        perf["total_tasks"] += 1
        if status == "success":
            perf["successful_tasks"] += 1
        else:
            perf["failed_tasks"] += 1
        
        # Обновление среднего времени
        total_duration = sum(t["duration"] for t in perf["tasks"])
        perf["average_duration"] = total_duration / len(perf["tasks"])
        
        # Ограничение истории
        if len(perf["tasks"]) > 500:
            perf["tasks"] = perf["tasks"][-500:]
            
    def get_request_statistics(
        self,
        request_type: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Получение статистики запросов
        
        Args:
            request_type: Тип запроса (если None, все типы)
            hours: Количество часов для анализа
            
        Returns:
            Статистика запросов
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if request_type:
            metrics = self.metrics.get(request_type, [])
        else:
            metrics = [m for metrics_list in self.metrics.values() for m in metrics_list]
        
        # Фильтрация по времени
        recent_metrics = [
            m for m in metrics
            if datetime.fromisoformat(m["timestamp"]) >= cutoff_time
        ]
        
        if not recent_metrics:
            return {
                "request_type": request_type or "all",
                "total_requests": 0
            }
        
        durations = [m["duration"] for m in recent_metrics]
        statuses = [m["status"] for m in recent_metrics]
        
        return {
            "request_type": request_type or "all",
            "total_requests": len(recent_metrics),
            "successful_requests": sum(1 for s in statuses if s == "success"),
            "failed_requests": sum(1 for s in statuses if s != "success"),
            "average_duration": float(sum(durations) / len(durations)),
            "min_duration": float(min(durations)),
            "max_duration": float(max(durations)),
            "p50_duration": float(sorted(durations)[len(durations) // 2]),
            "p95_duration": float(sorted(durations)[int(len(durations) * 0.95)]),
            "p99_duration": float(sorted(durations)[int(len(durations) * 0.99)])
        }
        
    def get_agent_performance(
        self,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Получение производительности агентов
        
        Args:
            agent_id: ID агента (если None, все агенты)
            
        Returns:
            Метрики производительности
        """
        if agent_id:
            return self.agent_performance.get(agent_id, {})
        
        return dict(self.agent_performance)
        
    def get_system_health(self) -> Dict[str, Any]:
        """
        Получение общего здоровья системы
        
        Returns:
            Метрики здоровья системы
        """
        # Статистика по всем типам запросов
        all_stats = self.get_request_statistics(hours=1)
        
        # Статистика агентов
        agent_stats = {}
        for agent_id, perf in self.agent_performance.items():
            agent_stats[agent_id] = {
                "total_tasks": perf["total_tasks"],
                "success_rate": perf["successful_tasks"] / perf["total_tasks"]
                if perf["total_tasks"] > 0 else 0,
                "average_duration": perf["average_duration"]
            }
        
        # Оценка здоровья
        health_score = 1.0
        
        # Штраф за высокую долю ошибок
        if all_stats.get("total_requests", 0) > 0:
            error_rate = all_stats.get("failed_requests", 0) / all_stats.get("total_requests", 1)
            if error_rate > 0.1:
                health_score -= 0.3
            elif error_rate > 0.05:
                health_score -= 0.15
        
        # Штраф за медленные запросы
        if all_stats.get("p95_duration", 0) > 5.0:  # > 5 секунд
            health_score -= 0.2
        elif all_stats.get("p95_duration", 0) > 2.0:  # > 2 секунды
            health_score -= 0.1
        
        health_score = max(health_score, 0.0)
        
        return {
            "health_score": float(health_score),
            "status": "healthy" if health_score > 0.7 else "degraded" if health_score > 0.4 else "unhealthy",
            "request_statistics": all_stats,
            "agent_performance": agent_stats,
            "active_requests": len(self.active_requests),
            "timestamp": datetime.now().isoformat()
        }


# Глобальный экземпляр
performance_monitor = PerformanceMonitor()

