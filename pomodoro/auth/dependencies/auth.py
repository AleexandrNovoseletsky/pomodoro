"""Зависимости авторизации."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from pomodoro.auth.permissions import require_owner, require_role
from pomodoro.auth.repositories.auth import AuthRepository
from pomodoro.auth.services.auth import AuthService
from pomodoro.core.exceptions.acces_denied import AccessDenied
from pomodoro.database.accesor import async_session_maker
from pomodoro.user.dependencies.user import (
    get_current_user,
    get_user_repository,
)
from pomodoro.user.repositories.user import UserRepository
from pomodoro.user.schemas.user import ResponseUserProfileSchema


def require_roles(allowed_roles: tuple[str, ...]) -> Callable:
    """Зависимость для роутов.

    Usage:
        Depends(require_roles(allowed_roles = ('root','admin'))).
    """

    async def _dep(
        current_user: Annotated[
            ResponseUserProfileSchema, Depends(get_current_user)
            ],
    ):
        if await require_role(
            current_user=current_user, allowed_roles=allowed_roles
        ):
            return current_user
        raise AccessDenied()

    return _dep


def require_owner_or_roles(
    resource_getter: Callable[..., object], allowed_roles: tuple[str, ...]
):
    """Зависимость возвращающая объект ресурса, например get_task_resource.

    Usage:
        Depends(require_owner_or_roles(get_task_resource, 'root', 'admin')).
    """

    async def _dep(
        current_user: Annotated[
            ResponseUserProfileSchema, Depends(get_current_user)
            ],
        resource: Annotated[object, Depends(resource_getter)],
    ):
        # если роль в allowed_roles — пропускаем
        if await require_role(current_user, allowed_roles):
            return current_user
        if await require_owner(resource, current_user):
            return current_user
        raise AccessDenied()

    return _dep


async def get_auth_repository(
) -> AuthRepository:
    """Получение репозитория авторизации."""
    return AuthRepository(sessionmaker=async_session_maker)


async def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    auth_repo: Annotated[AuthRepository, Depends(get_auth_repository)],
) -> AuthService:
    """Полуение сервиса авторизации."""
    return AuthService(user_repo=user_repo, auth_repo=auth_repo)
