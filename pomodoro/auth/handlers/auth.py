"""Authorization Endpoints.

REST API endpoints for user authentication and registration. Provides
login, registration, and OAuth integration with proper rate limiting and
security measures to prevent abuse.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter

from pomodoro.auth.dependencies.auth import get_auth_service
from pomodoro.auth.form import LoginForm
from pomodoro.auth.schemas.oauth import AccessTokenSchema
from pomodoro.auth.services.auth import AuthService
from pomodoro.user.dependencies.user import get_user_service
from pomodoro.user.schemas.user import (
    CreateUserProfileSchema,
    ResponseUserProfileSchema,
)
from pomodoro.user.services.user_service import UserProfileService

# Dependency annotations for consistent type checking and IDE support
auth_service_annotated = Annotated[
    AuthService, Depends(dependency=get_auth_service)
]

user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_user_service)
]

router = APIRouter()


@router.post(
    path="/register",
    response_model=ResponseUserProfileSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(RateLimiter(times=3, hours=24))],
    summary="Register new user",
    description=("Create a new user account. "
                 "Limit: no more than three registrations per day."),
)
async def register_user(
    body: CreateUserProfileSchema,
    user_service: user_service_annotated,
) -> ResponseUserProfileSchema:
    """User Registration.

    Returns:
        The scheme of the new user.
    """
    return await user_service.create_user(user_data=body)


@router.post(
    path="/login",
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    summary="User login by username and password",
    description=("User authentication by phone number and password. "
                 "Limit: five attempts per minute."),
)
async def login_user(
    auth_service: auth_service_annotated,
    form_data: Annotated[LoginForm, Depends()],
) -> AccessTokenSchema:
    """User Login.

    Returns:
        {
        "access_token": access_token,
        "token_type": bearer
        }
    """
    return await auth_service.login(
        phone=form_data.username, password=form_data.password
    )


@router.get(
    path="/login/yandex",
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    summary="Login with Yandex ID",
    description=("Redirect to Yandex OAuth authentication page. "
                 "Limit: five attempts per minute."),
)
async def yandex_login(auth_service: auth_service_annotated):
    """User Login via Yandex ID.

    After login redirected to an endpoint to an obtain an access token.
    """
    redirect_url = await auth_service.get_yandex_redirect_url()
    return RedirectResponse(url=redirect_url)


@router.get(
    path="/yandex",
    summary="Get access token via Yandex",
    description=("Callback endpoint "
                 "for processing response from Yandex OAuth "
                 "and obtaining access token."),
)
async def yandex_auth(
    code: str, auth_service: auth_service_annotated
) -> AccessTokenSchema:
    """Getting an access token.

    Returns:     dict {"access_token": access_token}
    """
    return await auth_service.get_yandex_auth(code=code)
