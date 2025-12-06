"""
ARIN Platform - Password Handler
Обработка паролей (хеширование и проверка)
"""
import logging
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class PasswordHandler:
    """
    Обработчик паролей с использованием bcrypt
    """
    
    def __init__(self):
        """Инициализация Password Handler"""
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def hash_password(self, password: str) -> str:
        """
        Хеширование пароля
        
        Args:
            password: Пароль в открытом виде
            
        Returns:
            Хешированный пароль
        """
        return self.pwd_context.hash(password)
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Проверка пароля
        
        Args:
            plain_password: Пароль в открытом виде
            hashed_password: Хешированный пароль
            
        Returns:
            True если пароль верный
        """
        return self.pwd_context.verify(plain_password, hashed_password)


# Глобальный экземпляр
password_handler = PasswordHandler()

