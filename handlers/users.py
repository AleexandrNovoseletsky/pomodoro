from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependencies import get_user_service, get_current_user
from auth import OAuth2PhoneRequestForm
from models import UserProfile
from schemas import (
    CreateUserProfileSchema,
    ResponseUserProfileSchema,
    LoginUserSchema,
)
from services.user_service import UserProfileService

current_user_annotated = Annotated[
    ResponseUserProfileSchema, Depends(dependency=get_current_user)
]
router = APIRouter(prefix="/users", tags=["users"])
user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_user_service)
]


@router.get(path="/", response_model=list[ResponseUserProfileSchema])
async def get_users(
    user_service: user_service_annotated,
) -> list[ResponseUserProfileSchema]:
    return await user_service.get_all_objects()


@router.get(path="/me", response_model=ResponseUserProfileSchema)
async def get_me(current_user: current_user_annotated):
    return current_user


@router.post(
    path="/register",
    response_model=ResponseUserProfileSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    body: CreateUserProfileSchema,
    user_service: user_service_annotated,
) -> UserProfile:
    return await user_service.register_user(user_data=body)


@router.post(path="/login")
async def login_user(
    user_service: user_service_annotated,
    form_data: OAuth2PhoneRequestForm = Depends(),
):
    return await user_service.login(
        login_data=LoginUserSchema(
            phone=form_data.phone, password=form_data.password
        )
    )
