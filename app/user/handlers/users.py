"""Роуты для управления пользователями и аутентификацией.

Handlers используют зависимости `get_user_service` и `get_current_user`.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies.auth import require_roles
from app.user.dependencies.user import get_current_user, get_user_service
from app.user.models.users import UserProfile, UserRole
from app.user.schemas.user import (
    ResponseUserProfileSchema,
    UpdateUserProfileSchema,
)
from app.user.services.user_service import UserProfileService

current_user_annotated = Annotated[
    UserProfile, Depends(dependency=get_current_user)
]
router = APIRouter()

user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_user_service)
]

admin = UserRole.ADMIN
root = UserRole.ROOT


@router.get(path="/", response_model=list[ResponseUserProfileSchema])
async def get_users(
    user_service: user_service_annotated,
) -> list[ResponseUserProfileSchema]:
    return await user_service.get_all_objects()


@router.get(path="/me", response_model=ResponseUserProfileSchema)
async def get_me(current_user: current_user_annotated):
    return current_user


@router.patch(path="/me", response_model=ResponseUserProfileSchema)
async def update_me(
    body: UpdateUserProfileSchema,
    current_user: current_user_annotated,
    user_service: user_service_annotated,
):
    return await user_service.update_me(
        current_user=current_user, update_data=body
    )


@router.patch(
    path="/{user_id}",
    response_model=ResponseUserProfileSchema,
    dependencies=[
        Depends(dependency=require_roles(allowed_roles=(root, admin)))
    ],
)
async def update_user(
    user_id: int,
    body: UpdateUserProfileSchema,
    current_user: current_user_annotated,
    user_service: user_service_annotated,
):
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
    await user_service.delete_object(object_id=user_id)
