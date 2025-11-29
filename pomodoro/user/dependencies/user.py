"""User dependencies.

Dependency injection configuration for user-related components and
authentication. Provides factory functions for user repositories,
services, and JWT token validation with proper error handling and
security measures.
"""

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


async def get_user_repository() -> UserRepository:
    """Create and return user repository instance.

    Returns:     UserRepository: Repository instance configured with
    database session maker     for performing user database operations.

    Note:     Uses application-wide async session maker for consistent
    database connectivity.     Repository is created per request for
    proper connection lifecycle management.
    """
    return UserRepository(sessionmaker=async_session_maker)


async def get_user_service(
    user_repo: Annotated[
        UserRepository, Depends(dependency=get_user_repository)
    ],
    media_service: Annotated[MediaService, Depends(get_media_service)],
) -> UserProfileService:
    """Create and return user service instance with dependencies.

    Args:     user_repo: Injected user repository for data operations
    media_service: Injected media service for file management

    Returns:     UserProfileService: Fully configured service instance
    for handling user     business logic, profile management, and media
    operations.
    """
    return UserProfileService(user_repo=user_repo, media_service=media_service)


async def get_current_user(
    service: Annotated[UserProfileService, Depends(get_user_service)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserProfile:
    """Retrieve current authenticated user from JWT token.

    Validates JWT token, extracts user ID, and retrieves complete user
    profile from database. Used as dependency in protected endpoints.

    Args:     service: Injected user service for profile retrieval
    token: JWT token from Authorization header

    Returns:     UserPro
    file:
    Complete user profile of authenticated user

    Raises:
    HTTPException: 401 Unauthorized for invalid, expired, or malformed tokens
    or if user no longer exists in database

    Note:
    Implements proper JWT validation with comprehensive error handling
    for various token-related failure scenarios.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (JWTError, ExpiredSignatureError, ValueError, KeyError) as err:
        raise credentials_exception from err

    # Retrieve user profile from database
    current_user = await service.get_one_object(object_id=user_id)
    if current_user is None:
        raise credentials_exception
    return current_user
