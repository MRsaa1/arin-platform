"""
ARIN Platform - Authentication API
API endpoints для аутентификации и авторизации
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional

from backend.auth.jwt_handler import JWTHandler, Token, get_current_user, TokenData
from backend.auth.password_handler import PasswordHandler
from backend.auth.oauth import OAuthHandler
from backend.auth.api_keys import APIKeyManager, api_key_manager
from backend.auth.rbac import require_permission, Permission

router = APIRouter()

jwt_handler = JWTHandler()
password_handler = PasswordHandler()
oauth_handler = OAuthHandler()


class UserCreate(BaseModel):
    """Модель создания пользователя"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Модель входа пользователя"""
    username: str
    password: str


class OAuthLogin(BaseModel):
    """Модель OAuth входа"""
    provider: str  # github, google
    token: str


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """
    Регистрация нового пользователя
    
    В production здесь должна быть проверка уникальности и сохранение в БД
    """
    # TODO: Проверка уникальности username/email
    # TODO: Сохранение в БД
    
    # Хеширование пароля
    hashed_password = password_handler.hash_password(user_data.password)
    
    # Создание токена
    access_token = jwt_handler.create_access_token(
        data={
            "sub": user_data.username,
            "user_id": "user_id_here",  # TODO: Реальный ID из БД
            "roles": ["viewer"]  # По умолчанию роль viewer
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=jwt_handler.access_token_expire_minutes * 60
    )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Вход пользователя (OAuth2 password flow)
    """
    # TODO: Проверка пользователя в БД
    # TODO: Проверка пароля
    
    # Временная заглушка для демонстрации
    # В production здесь должна быть проверка в БД
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Создание токена
    access_token = jwt_handler.create_access_token(
        data={
            "sub": form_data.username,
            "user_id": "admin_id",
            "roles": ["admin", "analyst"]
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=jwt_handler.access_token_expire_minutes * 60
    )


@router.post("/oauth", response_model=Token)
async def oauth_login(oauth_data: OAuthLogin):
    """
    OAuth 2.0 вход (GitHub, Google)
    """
    user_data = None
    
    if oauth_data.provider == "github":
        user_data = await oauth_handler.verify_github_token(oauth_data.token)
    elif oauth_data.provider == "google":
        user_data = await oauth_handler.verify_google_token(oauth_data.token)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {oauth_data.provider}"
        )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OAuth token"
        )
    
    # TODO: Создание/обновление пользователя в БД
    
    # Создание токена
    access_token = jwt_handler.create_access_token(
        data={
            "sub": user_data["username"],
            "user_id": user_data.get("email"),
            "roles": ["viewer"]  # По умолчанию
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=jwt_handler.access_token_expire_minutes * 60
    )


@router.get("/me")
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user)
):
    """Получение информации о текущем пользователе"""
    return {
        "username": current_user.username,
        "user_id": current_user.user_id,
        "roles": current_user.roles
    }


@router.post("/api-keys")
async def create_api_key(
    name: str,
    permissions: list = [],
    expires_days: Optional[int] = None,
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """
    Создание нового API ключа
    
    Требует разрешение MANAGE_SYSTEM
    """
    key_id, api_key = api_key_manager.create_api_key(
        name=name,
        user_id=current_user.user_id,
        permissions=permissions,
        expires_days=expires_days
    )
    
    return {
        "key_id": key_id,
        "api_key": api_key,  # Показать только один раз!
        "name": name,
        "created_at": api_key_manager.keys[key_id].created_at.isoformat(),
        "expires_at": api_key_manager.keys[key_id].expires_at.isoformat() if api_key_manager.keys[key_id].expires_at else None
    }


@router.get("/api-keys")
async def list_api_keys(
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Список API ключей"""
    keys = api_key_manager.list_api_keys(user_id=current_user.user_id)
    
    return {
        "keys": [
            {
                "key_id": k.key_id,
                "name": k.name,
                "created_at": k.created_at.isoformat(),
                "expires_at": k.expires_at.isoformat() if k.expires_at else None,
                "last_used": k.last_used.isoformat() if k.last_used else None,
                "is_active": k.is_active
            }
            for k in keys
        ]
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: TokenData = Depends(require_permission(Permission.MANAGE_SYSTEM))
):
    """Отзыв API ключа"""
    if api_key_manager.revoke_api_key(key_id):
        return {"message": f"API key {key_id} revoked"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

