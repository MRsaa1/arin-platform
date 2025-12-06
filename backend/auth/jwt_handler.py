"""
ARIN Platform - JWT Handler
Обработка JWT токенов для аутентификации
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from backend.config import settings

logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    """Модель токена"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Данные из токена"""
    username: Optional[str] = None
    user_id: Optional[str] = None
    roles: list = []


class JWTHandler:
    """
    Обработчик JWT токенов
    """
    
    def __init__(self):
        """Инициализация JWT Handler"""
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Создание JWT токена
        
        Args:
            data: Данные для включения в токен
            expires_delta: Время жизни токена
            
        Returns:
            JWT токен
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
        
    def verify_token(self, token: str) -> Optional[TokenData]:
        """
        Проверка и декодирование JWT токена
        
        Args:
            token: JWT токен
            
        Returns:
            Данные из токена или None
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            roles: list = payload.get("roles", [])
            
            if username is None:
                return None
                
            return TokenData(
                username=username,
                user_id=user_id,
                roles=roles
            )
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
            
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Декодирование токена без проверки (для отладки)
        
        Args:
            token: JWT токен
            
        Returns:
            Декодированные данные
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_signature": False}
            )
            return payload
        except JWTError as e:
            logger.error(f"Token decode failed: {e}")
            return {}


# Глобальный экземпляр
jwt_handler = JWTHandler()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependency для получения текущего пользователя из JWT токена
    
    Args:
        token: JWT токен из заголовка Authorization
        
    Returns:
        Данные пользователя
        
    Raises:
        HTTPException: Если токен невалиден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = jwt_handler.verify_token(token)
    if token_data is None:
        raise credentials_exception
        
    return token_data


async def get_current_active_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency для получения активного пользователя
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        Активный пользователь
        
    Raises:
        HTTPException: Если пользователь неактивен
    """
    # Здесь можно добавить проверку активности пользователя в БД
    # Пока что просто возвращаем пользователя
    return current_user

