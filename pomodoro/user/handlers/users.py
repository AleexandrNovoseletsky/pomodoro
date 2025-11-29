"""User management routes.

Provides REST API endpoints for user profile management and
administration. Includes routes for self-service operations and
administrative functions with proper role-based access control.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from pomodoro.auth.dependencies.auth import require_roles
from pomodoro.user.dependencies.user import get_current_user, get_user_service
from pomodoro.user.models.users import UserProfile, UserRole
from pomodoro.user.schemas.user import (
    ResponseUserProfileSchema,
    UpdateUserProfileSchema,
)
from pomodoro.user.services.user_service import UserProfileService

# Current authenticated user dependency
current_user_annotated = Annotated[
    UserProfile, Depends(dependency=get_current_user)
]

# User service dependency
user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_user_service)
]

# Role constants for dependency configuration
admin = UserRole.ADMIN
root = UserRole.ROOT

router = APIRouter()


@router.get(
    path="/",
    response_model=list[ResponseUserProfileSchema],
    summary="Получить всех пользователей",
    description=("Возвращает список всех пользователей в системе. "
                 "Требуются права администратора."),
)
async def get_users(
    user_service: user_service_annotated,
) -> list[ResponseUserProfileSchema]:
    """Get all users."""
    return await user_service.get_all_objects()


@router.get(
    path="/me",
    response_model=ResponseUserProfileSchema,
    summary="Получить информацию о текущем пользователе",
    description=("Возвращает профиль пользователя, сделавшего запрос. "
                 "Доступно всем авторизованным пользователям."),
)
async def get_me(
    current_user: current_user_annotated,
) -> ResponseUserProfileSchema:
    """Get information about the user who made the request."""
    return ResponseUserProfileSchema.model_validate(current_user)


@router.patch(
    path="/me",
    response_model=ResponseUserProfileSchema,
    summary="Обновить данные текущего пользователя",
    description=("Обновление профиля пользователя, сделавшего запрос. "
                 "Доступно всем авторизованным пользователям."),
)
async def update_me(
    body: UpdateUserProfileSchema,
    current_user: current_user_annotated,
    user_service: user_service_annotated,
) -> ResponseUserProfileSchema:
    """Update data about the user who made the request."""
    return await user_service.update_me(
        current_user=current_user, update_data=body
    )


@router.patch(
    path="/{user_id}",
    response_model=ResponseUserProfileSchema,
    dependencies=[
        Depends(dependency=require_roles(allowed_roles=(root, admin))),
    ],
    summary="Обновить данные пользователя",
    description=("Обновление профиля любого пользователя в системе. "
                 "Требуются права администратора или root."),
)
async def update_user(
    user_id: int,
    body: UpdateUserProfileSchema,
    current_user: current_user_annotated,
    user_service: user_service_annotated,
) -> ResponseUserProfileSchema:
    """Update user data.

    Available to administrators.
    """
    return await user_service.update_user(
        user_id=user_id, current_user=current_user, update_data=body
    )


@router.delete(
    path="/delete/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependency=require_roles(allowed_roles=(root,)))],
    summary="Удалить пользователя",
    description=("Полное удаление пользователя из системы. "
                 "Требуются права root-пользователя."),
)
async def delete_user(
    user_id: int,
    user_service: user_service_annotated,
) -> None:
    """Delete user.

    Available to root only.
    """
    await user_service.delete_object(object_id=user_id)
