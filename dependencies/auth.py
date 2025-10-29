from typing import Callable
from fastapi import Depends

from auth import require_role, require_owner
from custom_exceptions import AccessDenied
from dependencies.user import get_current_user


def require_roles(allowed_roles: tuple[str, ...]) -> Callable:
    """Зависимость для роутов: Depends(require_roles(allowed_roles = ('root','admin')))"""

    async def _dep(current_user: dict = Depends(get_current_user)):
        if await require_role(current_user, allowed_roles):
            return current_user
        raise AccessDenied()

    return _dep


def require_owner_or_roles(
    resource_getter: Callable[..., object], allowed_roles: tuple[str, ...]
):
    """
    resource_getter — зависимость, которая возвращает объект ресурса (например get_task_resource).
    Usage:
        Depends(require_owner_or_roles(get_task_resource, 'root', 'admin'))
    """

    async def _dep(
        current_user: dict = Depends(get_current_user),
        resource: object = Depends(resource_getter),
    ):
        # если роль в allowed_roles — пропускаем
        if await require_role(current_user, allowed_roles):
            return current_user
        if await require_owner(resource, current_user):
            return current_user
        raise AccessDenied()

    return _dep
