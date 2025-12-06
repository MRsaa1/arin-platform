"""
ARIN Platform - Base Agent Class
Базовый класс для всех агентов
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import asyncio
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Статусы агента"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    ANALYZING = "analyzing"
    LEARNING = "learning"
    REPORTING = "reporting"
    ERROR = "error"


class BaseAgent(ABC):
    """Базовый класс для всех агентов ARIN"""
    
    def __init__(self, agent_id: str, agent_name: str, config: Dict[str, Any]):
        """
        Инициализация агента
        
        Args:
            agent_id: Уникальный ID агента
            agent_name: Имя агента
            config: Конфигурация агента
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.config = config
        self.status = AgentStatus.INITIALIZING
        self.task_queue = asyncio.Queue()
        self.metrics = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "last_task_time": None,
            "average_processing_time": 0.0
        }
        self._running = False
        
    async def initialize(self):
        """Инициализация агента"""
        try:
            self.status = AgentStatus.INITIALIZING
            logger.info(f"Initializing agent {self.agent_name} ({self.agent_id})")
            
            await self._setup_data_access()
            await self._setup_ai_integration()
            
            self.status = AgentStatus.IDLE
            logger.info(f"Agent {self.agent_name} initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_name}: {e}")
            self.status = AgentStatus.ERROR
            raise
        
    @abstractmethod
    async def _setup_data_access(self):
        """Настройка доступа к данным"""
        pass
        
    @abstractmethod
    async def _setup_ai_integration(self):
        """Настройка AI интеграции"""
        pass
        
    @abstractmethod
    async def analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Основной метод анализа
        
        Args:
            task: Задача для анализа
            
        Returns:
            Результаты анализа
        """
        pass
        
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка задачи
        
        Args:
            task: Задача для обработки
            
        Returns:
            Результаты обработки
        """
        start_time = datetime.now()
        task_id = task.get("task_id", str(uuid.uuid4()))
        
        try:
            self.status = AgentStatus.ANALYZING
            logger.info(f"Agent {self.agent_name} processing task {task_id}")
            
            result = await self.analyze(task)
            
            self.status = AgentStatus.REPORTING
            await self._report_result(result)
            
            # Обновление метрик
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(processing_time, success=True)
            
            self.status = AgentStatus.IDLE
            logger.info(f"Agent {self.agent_name} completed task {task_id} in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(processing_time, success=False)
            
            logger.error(f"Agent {self.agent_name} failed to process task {task_id}: {e}")
            await self._handle_error(e, task)
            raise
            
    @abstractmethod
    async def _report_result(self, result: Dict[str, Any]):
        """
        Отчет о результатах
        
        Args:
            result: Результаты анализа
        """
        pass
        
    async def _handle_error(self, error: Exception, task: Optional[Dict[str, Any]] = None):
        """
        Обработка ошибок
        
        Args:
            error: Ошибка
            task: Задача, при обработке которой произошла ошибка
        """
        logger.error(f"Error in agent {self.agent_name}: {error}", exc_info=True)
        
        # Попытка восстановления
        try:
            await asyncio.sleep(1)  # Небольшая задержка перед восстановлением
            self.status = AgentStatus.IDLE
        except Exception as e:
            logger.error(f"Failed to recover agent {self.agent_name}: {e}")
            
    def _update_metrics(self, processing_time: float, success: bool):
        """Обновление метрик агента"""
        self.metrics["last_task_time"] = datetime.now().isoformat()
        
        if success:
            self.metrics["tasks_processed"] += 1
        else:
            self.metrics["tasks_failed"] += 1
            
        # Обновление среднего времени обработки
        total_tasks = self.metrics["tasks_processed"] + self.metrics["tasks_failed"]
        if total_tasks > 0:
            current_avg = self.metrics["average_processing_time"]
            self.metrics["average_processing_time"] = (
                (current_avg * (total_tasks - 1) + processing_time) / total_tasks
            )
        
    async def run(self):
        """Основной цикл агента"""
        await self.initialize()
        self._running = True
        
        logger.info(f"Agent {self.agent_name} started")
        
        while self._running:
            try:
                # Получение задачи из очереди с таймаутом
                try:
                    task = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=1.0
                    )
                    await self.process_task(task)
                except asyncio.TimeoutError:
                    # Нет задач, продолжаем ожидание
                    continue
                    
            except Exception as e:
                await self._handle_error(e)
                await asyncio.sleep(5)  # Задержка перед следующей попыткой
                
    async def stop(self):
        """Остановка агента"""
        logger.info(f"Stopping agent {self.agent_name}")
        self._running = False
        
    def get_status(self) -> Dict[str, Any]:
        """Получение статуса агента"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "metrics": self.metrics.copy()
        }

