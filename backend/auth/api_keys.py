"""
ARIN Platform - API Keys Management
Управление API ключами для интеграций
"""
import logging
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class APIKey(BaseModel):
    """Модель API ключа"""
    key_id: str
    key_hash: str  # Хешированный ключ
    name: str
    user_id: Optional[str] = None
    permissions: list = []
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True


class APIKeyManager:
    """
    Менеджер API ключей
    """
    
    def __init__(self):
        """Инициализация API Key Manager"""
        self.keys: Dict[str, APIKey] = {}  # В production использовать БД
        
    def generate_api_key(self, prefix: str = "arin") -> str:
        """
        Генерация нового API ключа
        
        Args:
            prefix: Префикс для ключа
            
        Returns:
            API ключ в формате: arin_xxxxxxxxxxxxxxxx
        """
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"
        
    def create_api_key(
        self,
        name: str,
        user_id: Optional[str] = None,
        permissions: list = None,
        expires_days: Optional[int] = None
    ) -> tuple[str, str]:
        """
        Создание нового API ключа
        
        Args:
            name: Название ключа
            user_id: ID пользователя
            permissions: Список разрешений
            expires_days: Количество дней до истечения
            
        Returns:
            (key_id, api_key) - ID ключа и сам ключ (показать только один раз!)
        """
        from backend.auth.password_handler import password_handler
        
        api_key = self.generate_api_key()
        key_hash = password_handler.hash_password(api_key)
        key_id = secrets.token_urlsafe(16)
        
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        api_key_obj = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            user_id=user_id,
            permissions=permissions or [],
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_active=True
        )
        
        self.keys[key_id] = api_key_obj
        
        logger.info(f"API key created: {name} (ID: {key_id})")
        
        return key_id, api_key
        
    def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """
        Проверка API ключа
        
        Args:
            api_key: API ключ для проверки
            
        Returns:
            APIKey объект или None
        """
        from backend.auth.password_handler import password_handler
        
        for key_id, key_obj in self.keys.items():
            if not key_obj.is_active:
                continue
                
            if key_obj.expires_at and key_obj.expires_at < datetime.utcnow():
                continue
                
            if password_handler.verify_password(api_key, key_obj.key_hash):
                # Обновление времени последнего использования
                key_obj.last_used = datetime.utcnow()
                return key_obj
                
        return None
        
    def revoke_api_key(self, key_id: str) -> bool:
        """
        Отзыв API ключа
        
        Args:
            key_id: ID ключа
            
        Returns:
            True если успешно
        """
        if key_id in self.keys:
            self.keys[key_id].is_active = False
            logger.info(f"API key revoked: {key_id}")
            return True
        return False
        
    def list_api_keys(self, user_id: Optional[str] = None) -> list[APIKey]:
        """
        Список API ключей
        
        Args:
            user_id: Фильтр по пользователю
            
        Returns:
            Список API ключей
        """
        keys = list(self.keys.values())
        
        if user_id:
            keys = [k for k in keys if k.user_id == user_id]
            
        return keys


# Глобальный экземпляр
api_key_manager = APIKeyManager()

