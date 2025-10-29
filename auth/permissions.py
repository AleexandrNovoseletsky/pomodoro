from typing import Any


async def require_owner(resource: Any, current_user: dict) -> bool:
    """Проверяет, является ли current_user владельцем resource."""
    if resource.author_id == current_user["user_id"]:
        return True
    return False


async def require_role(current_user: dict, allowed_roles: tuple[str, ...]) -> bool:
    """Проверяет, является ли роль current_user допустимой."""
    if current_user["role"] in allowed_roles:
        return True
    return False
