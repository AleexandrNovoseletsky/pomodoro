"""Роуты для управления пользователями."""

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

# Получение текущего пользователя
current_user_annotated = Annotated[
    UserProfile, Depends(dependency=get_current_user)
]

user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_user_service)
]

admin = UserRole.ADMIN
root = UserRole.ROOT

router = APIRouter()


@router.get(path="/", response_model=list[ResponseUserProfileSchema])
async def get_users(
    user_service: user_service_annotated,
) -> list[ResponseUserProfileSchema]:
    """Получение всех пользователей."""
    return await user_service.get_all_objects()


@router.get(path="/me", response_model=ResponseUserProfileSchema)
async def get_me(
    current_user: current_user_annotated
) -> ResponseUserProfileSchema:
    """олучение информации о пользователе, сделавшем запрос."""
    return ResponseUserProfileSchema.model_validate(current_user)


@router.patch(path="/me", response_model=ResponseUserProfileSchema)
async def update_me(
    body: UpdateUserProfileSchema,
    current_user: current_user_annotated,
    user_service: user_service_annotated,
) -> ResponseUserProfileSchema:
    """Обновление данных о пользователе сделавшем запрос."""
    return await user_service.update_me(
        current_user=current_user, update_data=body
    )


@router.patch(
    path="/{user_id}",
    response_model=ResponseUserProfileSchema,
    dependencies=[
        Depends(dependency=require_roles(allowed_roles=(root, admin))),
    ],
)
async def update_user(
    user_id: int,
    body: UpdateUserProfileSchema,
    current_user: current_user_annotated,
    user_service: user_service_annotated,
) -> ResponseUserProfileSchema:
    """Обновление данных о пользователе. Досткпно администраторам."""
    return await user_service.update_user(
        user_id=user_id, current_user=current_user, update_data=body
    )


@router.delete(
    path="/delete/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependency=require_roles(allowed_roles=(root,)))],
)
async def delete_user(
    user_id: int,
    user_service: user_service_annotated,
) -> None:
    """даление пользователя, досткпно root."""
    await user_service.delete_object(object_id=user_id)
