from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependencies import get_user_service, get_current_user
from models import UserProfile
from schemas import CreateUserSchema, ResponseUserSchema, LoginUserSchema
from services.user_service import UserProfileService

current_user_annotated = Annotated[dict, Depends(dependency=get_current_user)]
router = APIRouter(prefix="/users", tags=["users"])
user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_user_service)
]


@router.get(path="/", response_model=list[ResponseUserSchema])
async def get_users(
    user_service: user_service_annotated,
) -> list[ResponseUserSchema]:
    return await user_service.get_all_objects()


@router.get(path="/me", response_model=ResponseUserSchema)
async def get_me(
    user_service: user_service_annotated, current_user: current_user_annotated
):
    return await user_service.get_one_object(object_id=current_user["user_id"])


@router.post(
    path="/register",
    response_model=ResponseUserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    body: CreateUserSchema,
    user_service: user_service_annotated,
) -> UserProfile:
    return await user_service.register_user(user_data=body)


@router.post(path="/login")
async def login_user(
    body: LoginUserSchema,
    user_service: user_service_annotated,
):
    return await user_service.login(login_data=body)
