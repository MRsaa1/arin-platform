"""
ARIN Platform - Audit Middleware
Автоматическое логирование всех HTTP запросов
"""
import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.compliance.audit_logger import audit_logger, AuditEventType

logger = None  # Будет инициализирован при первом использовании


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware для автоматического audit logging всех запросов
    """
    
    async def dispatch(self, request: Request, call_next):
        """Обработка запроса с audit logging"""
        global logger
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        
        # Получение информации о пользователе из токена (если есть)
        user_id = None
        username = None
        
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
                from backend.auth.jwt_handler import jwt_handler
                token_data = jwt_handler.verify_token(token)
                if token_data:
                    user_id = token_data.user_id
                    username = token_data.username
        except Exception:
            pass  # Игнорируем ошибки при извлечении токена
        
        # Определение типа события на основе endpoint
        event_type = self._determine_event_type(request.method, request.url.path)
        
        # Выполнение запроса
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Логирование события
        audit_logger.log_event(
            event_type=event_type,
            user_id=user_id,
            username=username,
            resource_type=self._extract_resource_type(request.url.path),
            resource_id=self._extract_resource_id(request.url.path),
            action=f"{request.method} {request.url.path}",
            details={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration": duration
            },
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=200 <= response.status_code < 400,
            error_message=None if 200 <= response.status_code < 400 else f"HTTP {response.status_code}"
        )
        
        return response
        
    def _determine_event_type(self, method: str, path: str) -> AuditEventType:
        """Определение типа события на основе метода и пути"""
        # Аутентификация
        if "/auth/login" in path:
            return AuditEventType.LOGIN if method == "POST" else AuditEventType.DATA_ACCESSED
        if "/auth/logout" in path:
            return AuditEventType.LOGOUT
        if "/auth/api-keys" in path:
            if method == "POST":
                return AuditEventType.API_KEY_CREATED
            elif method == "DELETE":
                return AuditEventType.API_KEY_REVOKED
            else:
                return AuditEventType.API_KEY_USED
        
        # Риски
        if "/risks/analyze" in path:
            return AuditEventType.RISK_ANALYZED
        if "/risks" in path:
            if method == "DELETE":
                return AuditEventType.RISK_DELETED
            else:
                return AuditEventType.RISK_VIEWED
        
        # Агенты
        if "/agents" in path:
            if "/start" in path:
                return AuditEventType.AGENT_STARTED
            elif "/stop" in path:
                return AuditEventType.AGENT_STOPPED
            else:
                return AuditEventType.DATA_ACCESSED
        
        # Граф
        if "/graph" in path:
            if method == "POST" or method == "PUT":
                return AuditEventType.GRAPH_UPDATED
            else:
                return AuditEventType.DATA_ACCESSED
        
        # ML Models
        if "/ml/train" in path:
            return AuditEventType.MODEL_TRAINED
        if "/ml" in path:
            return AuditEventType.MODEL_EVALUATED
        
        # Данные
        if "/gdpr/export" in path or "/audit-logs/export" in path:
            return AuditEventType.DATA_EXPORTED
        if "/gdpr/data" in path and method == "DELETE":
            return AuditEventType.DATA_DELETED
        
        # По умолчанию
        return AuditEventType.DATA_ACCESSED
        
    def _extract_resource_type(self, path: str) -> str:
        """Извлечение типа ресурса из пути"""
        if "/agents" in path:
            return "agent"
        if "/risks" in path:
            return "risk_analysis"
        if "/graph" in path:
            return "graph"
        if "/ml" in path:
            return "ml_model"
        if "/auth" in path:
            return "authentication"
        return "system"
        
    def _extract_resource_id(self, path: str) -> str:
        """Извлечение ID ресурса из пути"""
        parts = path.split("/")
        # Ищем UUID или числовой ID в пути
        for part in parts:
            if len(part) > 10 and (part.replace("-", "").replace("_", "").isalnum()):
                return part
        return None

