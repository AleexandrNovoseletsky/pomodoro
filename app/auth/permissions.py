"""Разрешения авторизации."""

from typing import Any

from app.user.schemas.user import ResponseUserProfileSchema


async def require_owner(
    resource: Any, current_user: ResponseUserProfileSchema
) -> bool:
    """Проверяет, является ли current_user владельцем resource."""
    if resource.author_id == current_user.id:
        return True
    return False


async def require_role(
    current_user: ResponseUserProfileSchema, allowed_roles: tuple[str, ...]
) -> bool:
    """Проверяет, является ли роль current_user допустимой."""
    if current_user.role in allowed_roles:
        return True
    return False
