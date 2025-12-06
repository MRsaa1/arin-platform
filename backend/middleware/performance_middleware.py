"""
ARIN Platform - Performance Monitoring Middleware
Middleware для отслеживания производительности запросов
"""
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.services.performance_monitor import performance_monitor

logger = None  # Будет инициализирован при первом использовании


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware для мониторинга производительности запросов
    """
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с мониторингом"""
        global logger
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        
        # Генерация ID запроса
        request_id = str(uuid.uuid4())
        
        # Определение типа запроса
        request_type = f"{request.method} {request.url.path}"
        
        # Начало отслеживания
        performance_monitor.start_request(request_id, request_type)
        
        try:
            # Выполнение запроса
            response = await call_next(request)
            
            # Определение статуса
            status = "success" if response.status_code < 400 else "error"
            
            # Завершение отслеживания
            performance_monitor.end_request(request_id, status)
            
            # Добавление заголовков с метриками
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Ошибка при обработке
            performance_monitor.end_request(request_id, "error")
            raise

