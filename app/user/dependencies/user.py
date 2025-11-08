from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.accesor import get_db_session
from app.user.repositories.user import UserRepository
from app.user.schemas.user import ResponseUserProfileSchema
from app.user.services.user_service import UserProfileService
from app.core.settings import Settings

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


async def get_user_repository(
    db: AsyncSession = Depends(get_db_session),
) -> UserRepository:
    return UserRepository(db_session=db)


async def get_user_service(
    user_repo: UserRepository = Depends(dependency=get_user_repository),
) -> UserProfileService:
    return UserProfileService(user_repo=user_repo)


async def get_current_user(
    service: UserProfileService = Depends(get_user_service),
    token: str = Depends(oauth2_scheme),
) -> ResponseUserProfileSchema:
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
    except Exception:
        raise credentials_exception
    current_user = await service.get_one_object(object_id=user_id)
    if current_user is None:
        raise credentials_exception
    return current_user
