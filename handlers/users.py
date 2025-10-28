from fastapi import APIRouter, Depends

from dependencies import get_user_service
from models import UserProfile
from schemas import CreateUserSchema, ResponseUserSchema, LoginUserSchema
from services.user_service import UserProfileService

router = APIRouter(prefix='/users', tags=['users'])


@router.get(path='/', response_model=list[ResponseUserSchema])
async def get_users(
        user_service: UserProfileService = Depends(get_user_service)
) -> list[ResponseUserSchema]:
    return await user_service.get_all_objects()


@router.post(path='/register', response_model=ResponseUserSchema)
async def register_user(
        new_user: CreateUserSchema,
        user_service: UserProfileService = Depends(get_user_service)
) -> UserProfile:
    return await user_service.register_user(new_user)


@router.post(path='/login')
async def login_user(
        login_data: LoginUserSchema,
        user_service: UserProfileService = Depends(get_user_service)
):
    return await user_service.login(login_data=login_data)
