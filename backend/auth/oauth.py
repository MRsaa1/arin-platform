"""
ARIN Platform - OAuth Handler
Обработка OAuth 2.0 аутентификации
"""
import logging
from typing import Optional, Dict, Any
import httpx

from backend.config import settings

logger = logging.getLogger(__name__)


class OAuthHandler:
    """
    Обработчик OAuth 2.0 аутентификации
    Поддерживает GitHub, Google, Microsoft
    """
    
    def __init__(self):
        """Инициализация OAuth Handler"""
        self.github_client_id: Optional[str] = None
        self.github_client_secret: Optional[str] = None
        self.google_client_id: Optional[str] = None
        self.google_client_secret: Optional[str] = None
        
    async def verify_github_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Проверка GitHub OAuth токена
        
        Args:
            token: GitHub OAuth токен
            
        Returns:
            Данные пользователя или None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"token {token}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "username": user_data.get("login"),
                        "email": user_data.get("email"),
                        "name": user_data.get("name"),
                        "avatar_url": user_data.get("avatar_url"),
                        "provider": "github"
                    }
                else:
                    logger.warning(f"GitHub token verification failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"GitHub OAuth verification error: {e}")
            return None
            
    async def verify_google_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Проверка Google OAuth токена
        
        Args:
            token: Google OAuth токен
            
        Returns:
            Данные пользователя или None
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return {
                        "username": user_data.get("email", "").split("@")[0],
                        "email": user_data.get("email"),
                        "name": user_data.get("name"),
                        "avatar_url": user_data.get("picture"),
                        "provider": "google"
                    }
                else:
                    logger.warning(f"Google token verification failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Google OAuth verification error: {e}")
            return None


# Глобальный экземпляр
oauth_handler = OAuthHandler()

