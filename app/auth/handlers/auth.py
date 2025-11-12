from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from app.auth.dependencies.auth import get_auth_service
from app.auth.form import OAuth2PhoneRequestForm
from app.auth.services.auth import AuthService
from app.core.repositories.base_crud import HasId
from app.user.schemas.user import (
    CreateUserProfileSchema,
    LoginUserSchema,
    ResponseUserProfileSchema,
)
from app.user.services.user_service import UserProfileService

router = APIRouter()

auth_service_annotated = Annotated[
    AuthService, Depends(dependency=get_auth_service)
]
user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_auth_service)
]


@router.post(
    path="/register",
    response_model=ResponseUserProfileSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    body: CreateUserProfileSchema,
    auth_service: auth_service_annotated,
) -> HasId:
    return await auth_service.register_user(user_data=body)


@router.post(path="/login")
async def login_user(
    auth_service: auth_service_annotated,
    form_data: OAuth2PhoneRequestForm = Depends(),
):
    return await auth_service.login(
        login_data=LoginUserSchema(
            phone=form_data.phone, password=form_data.password
        )
    )


@router.get(path="/login/yandex")
async def yandex_login(auth_service: auth_service_annotated):
    redirect_url = await auth_service.get_yandex_redirect_url()
    print(redirect_url)
    return RedirectResponse(url=redirect_url)


@router.get(path="/yandex")
async def yandex_auth(code: str, auth_service: auth_service_annotated):
    return await auth_service.get_yandex_auth(code=code)
