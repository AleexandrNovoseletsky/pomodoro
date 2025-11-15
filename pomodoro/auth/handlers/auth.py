"""Роуты авторизации."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse

from pomodoro.auth.dependencies.auth import get_auth_service
from pomodoro.auth.form import LoginForm
from pomodoro.auth.services.auth import AuthService
from pomodoro.user.schemas.user import (
    CreateUserProfileSchema,
    ResponseUserProfileSchema,
)
from pomodoro.user.services.user_service import UserProfileService

auth_service_annotated = Annotated[
    AuthService, Depends(dependency=get_auth_service)
]
user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_auth_service)
]

router = APIRouter()


@router.post(
    path="/register",
    response_model=ResponseUserProfileSchema,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    body: CreateUserProfileSchema,
    auth_service: auth_service_annotated,
) -> ResponseUserProfileSchema:
    """Регистрация пользователя."""
    return await auth_service.register_user(user_data=body)


@router.post(path="/login")
async def login_user(
    auth_service: auth_service_annotated,
    form_data: Annotated[LoginForm, Depends()],
) -> dict[str, str]:
    """Вход пользователя. Возвращает токен."""
    return await auth_service.login(
        phone=form_data.phone, password=form_data.password
        )


@router.get(path="/login/yandex")
async def yandex_login(auth_service: auth_service_annotated):
    """Вход пользователя через яндекс, первый этап."""
    redirect_url = await auth_service.get_yandex_redirect_url()
    return RedirectResponse(url=redirect_url)


@router.get(path="/yandex")
async def yandex_auth(
    code: str, auth_service: auth_service_annotated
) -> dict[str, str]:
    """Вход пользователя через Яндеес, второй этап. Возвращает токен."""
    return await auth_service.get_yandex_auth(code=code)
