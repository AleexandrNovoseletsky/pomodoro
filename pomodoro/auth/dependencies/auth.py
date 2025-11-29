"""Authorization dependencies.

Dependency injection configuration for authentication and authorization
components. Provides role-based and ownership-based access control
dependencies for FastAPI endpoints, along with service and repository
factories for authentication operations.
"""

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
from pomodoro.user.models.users import UserProfile, UserRole
from pomodoro.user.repositories.user import UserRepository


def require_roles(allowed_roles: tuple[UserRole, ...]) -> Callable:
    """Create dependency for role-based access control.

    Generates a FastAPI dependency that verifies the current user has
    one of the specified roles before granting access to the endpoint.

    Args:     allowed_roles: Tuple of user roles that are permitted to
    access the resource.         Example: (UserRole.ROOT,
    UserRole.ADMIN)

    Returns:     FastAPI dependency function that performs role
    validation

    Raises:     AccessDenied: If the current user's role is not in the
    allowed roles list

    Usage:     @router.get("/protected",
    dependencies=[Depends(require_roles((UserRole.ADMIN,)))])
    """

    async def _dep(
        current_user: Annotated[UserProfile, Depends(get_current_user)],
    ):
        if await require_role(
            current_user=current_user, allowed_roles=allowed_roles
        ):
            return current_user
        raise AccessDenied()

    return _dep


def require_owner_or_roles(
    resource_getter: Callable[..., object], allowed_roles: tuple[UserRole, ...]
) -> Callable:
    """Create dependency for combined ownership.

    Generates a FastAPI dependency that grants access if either: 1. The
    current user has one of the specified roles, OR 2. The current user
    is the owner of the resource

    Args:     resource_getter: Dependency function that returns the
    resource object         and provides access to ownership information
    allowed_roles: Tuple of user roles that are permitted to access the
    resource         Example: (UserRole.ROOT, UserRole.ADMIN)

    Returns:     FastAPI dependency function that performs combined
    validation

    Raises:     AccessDenied: If the user lacks both the required role
    and resource ownership

    Usage:     @router.patch("/tasks/{task_id}",
    dependencies=[Depends(require_owner_or_roles(
    resource_getter=get_task_resource,
    allowed_roles=(UserRole.ADMIN,)     ))])
    """

    async def _dep(
        current_user: Annotated[UserProfile, Depends(get_current_user)],
        resource: Annotated[Callable, Depends(resource_getter)],
    ):
        if await require_role(current_user, allowed_roles):
            return current_user
        if await require_owner(resource, current_user):
            return current_user
        raise AccessDenied()

    return _dep


async def get_auth_repository() -> AuthRepository:
    """Create and return authentication repository instance.

    Returns:     AuthRepository: Repository instance configured with
    database session maker     for performing authentication-related
    database operations.

    Note:     Uses application-wide async session maker for consistent
    database connectivity.     Repository is created per request for
    proper connection lifecycle management.
    """
    return AuthRepository(sessionmaker=async_session_maker)


async def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    auth_repo: Annotated[
        AuthRepository, Depends(dependency=get_auth_repository)
    ],
) -> AuthService:
    """Create and return authentication service instance.

    Args:     user_repo: Injected user repository for user data
    operations     auth_repo: Injected authentication repository for
    auth-specific operations

    Returns:     AuthService: Fully configured service instance for
    handling authentication     business logic, user registration, and
    login operations.
    """
    return AuthService(user_repo=user_repo, auth_repo=auth_repo)
