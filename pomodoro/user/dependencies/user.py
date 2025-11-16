"""Зависимости пользователей."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt

from pomodoro.core.settings import Settings
from pomodoro.database.accesor import async_session_maker
from pomodoro.media.dependencies.media import get_media_service
from pomodoro.media.services.media_service import MediaService
from pomodoro.user.models.users import UserProfile
from pomodoro.user.repositories.user import UserRepository
from pomodoro.user.services.user_service import UserProfileService

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_user_repository(
) -> UserRepository:
    """Получение репозитория пользователя."""
    return UserRepository(sessionmaker=async_session_maker)


async def get_user_service(
    user_repo: Annotated[
        UserRepository, Depends(dependency=get_user_repository)
        ],
    media_service: Annotated[MediaService, Depends(get_media_service)],
) -> UserProfileService:
    """Получение сервиса пользователя."""
    return UserProfileService(user_repo=user_repo, media_service=media_service)


async def get_current_user(
    service: Annotated[UserProfileService, Depends(get_user_service)],
    token: Annotated[str, Depends(oauth2_scheme)]
) -> UserProfile:
    """Получение пользователя сделавшего запрос."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (JWTError, ExpiredSignatureError, ValueError, KeyError) as err:
        raise credentials_exception from err
    current_user = await service.get_one_object(object_id=user_id)
    if current_user is None:
        raise credentials_exception
    return current_user
