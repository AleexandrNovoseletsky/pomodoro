from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependencies import get_user_service
from models import UserProfile
from schemas import CreateUserSchema, ResponseUserSchema, LoginUserSchema
from services.user_service import UserProfileService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(path="/", response_model=list[ResponseUserSchema])
async def get_users(
    user_service: Annotated[UserProfileService, Depends(get_user_service)],
) -> list[ResponseUserSchema]:
    return await user_service.get_all_objects()


@router.post(
    path="/register",
    response_model=ResponseUserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    body: CreateUserSchema,
    user_service: Annotated[UserProfileService, Depends(get_user_service)],
) -> UserProfile:
    return await user_service.register_user(user_data=body)


@router.post(path="/login")
async def login_user(
    body: LoginUserSchema,
    user_service: Annotated[UserProfileService, Depends(get_user_service)],
):
    return await user_service.login(login_data=body)
