"""
ARIN Platform - Role-Based Access Control (RBAC)
Система управления доступом на основе ролей
"""
import logging
from typing import List, Optional
from enum import Enum
from fastapi import Depends, HTTPException, status

from backend.auth.jwt_handler import TokenData, get_current_user

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API_USER = "api_user"


class Permission(str, Enum):
    """Разрешения"""
    # Агенты
    VIEW_AGENTS = "view_agents"
    MANAGE_AGENTS = "manage_agents"
    
    # Риски
    VIEW_RISKS = "view_risks"
    ANALYZE_RISKS = "analyze_risks"
    MANAGE_RISKS = "manage_risks"
    
    # Граф
    VIEW_GRAPH = "view_graph"
    MANAGE_GRAPH = "manage_graph"
    
    # Алерты
    VIEW_ALERTS = "view_alerts"
    MANAGE_ALERTS = "manage_alerts"
    
    # ML Models
    VIEW_MODELS = "view_models"
    TRAIN_MODELS = "train_models"
    MANAGE_MODELS = "manage_models"
    
    # Performance
    VIEW_PERFORMANCE = "view_performance"
    
    # Admin
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM = "manage_system"


# Маппинг ролей на разрешения
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.VIEW_AGENTS,
        Permission.MANAGE_AGENTS,
        Permission.VIEW_RISKS,
        Permission.ANALYZE_RISKS,
        Permission.MANAGE_RISKS,
        Permission.VIEW_GRAPH,
        Permission.MANAGE_GRAPH,
        Permission.VIEW_ALERTS,
        Permission.MANAGE_ALERTS,
        Permission.VIEW_MODELS,
        Permission.TRAIN_MODELS,
        Permission.MANAGE_MODELS,
        Permission.VIEW_PERFORMANCE,
        Permission.MANAGE_USERS,
        Permission.MANAGE_SYSTEM,
    ],
    Role.ANALYST: [
        Permission.VIEW_AGENTS,
        Permission.VIEW_RISKS,
        Permission.ANALYZE_RISKS,
        Permission.VIEW_GRAPH,
        Permission.VIEW_ALERTS,
        Permission.VIEW_MODELS,
        Permission.TRAIN_MODELS,
        Permission.VIEW_PERFORMANCE,
    ],
    Role.VIEWER: [
        Permission.VIEW_AGENTS,
        Permission.VIEW_RISKS,
        Permission.VIEW_GRAPH,
        Permission.VIEW_ALERTS,
        Permission.VIEW_MODELS,
        Permission.VIEW_PERFORMANCE,
    ],
    Role.API_USER: [
        Permission.VIEW_AGENTS,
        Permission.ANALYZE_RISKS,
        Permission.VIEW_GRAPH,
        Permission.VIEW_ALERTS,
        Permission.VIEW_MODELS,
    ],
}


def get_user_permissions(user: TokenData) -> List[Permission]:
    """
    Получение разрешений пользователя на основе его ролей
    
    Args:
        user: Данные пользователя
        
    Returns:
        Список разрешений
    """
    permissions = set()
    
    for role_name in user.roles:
        try:
            role = Role(role_name)
            if role in ROLE_PERMISSIONS:
                permissions.update(ROLE_PERMISSIONS[role])
        except ValueError:
            logger.warning(f"Unknown role: {role_name}")
    
    return list(permissions)


def require_permission(permission: Permission):
    """
    Dependency для проверки разрешения
    
    Args:
        permission: Требуемое разрешение
        
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: TokenData = Depends(get_current_user)
    ) -> TokenData:
        user_permissions = get_user_permissions(current_user)
        
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required"
            )
        
        return current_user
    
    return permission_checker


def require_role(role: Role):
    """
    Dependency для проверки роли
    
    Args:
        role: Требуемая роль
        
    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: TokenData = Depends(get_current_user)
    ) -> TokenData:
        if role.value not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role.value}' required"
            )
        
        return current_user
    
    return role_checker

