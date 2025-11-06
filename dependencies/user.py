from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database.accesor import get_db_session
from models import UserProfile
from repositories.user import UserRepository
from services.user_service import UserProfileService
from settings import Settings

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_user_repository(db: Session = Depends(get_db_session)) -> UserRepository:
    return UserRepository(db_session=db)


async def get_user_service(
    user_repo: UserRepository = Depends(dependency=get_user_repository),
) -> UserProfileService:
    return UserProfileService(repository=user_repo)


async def get_current_user(
    service=Depends(dependency=get_user_service),
    token: str = Depends(dependency=oauth2_scheme),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id: str = payload["sub"]
        current_user: UserProfile = await service.get_one_object(object_id=int(user_id))
        if user_id is None or current_user is None:
            raise credentials_exception
        role = current_user.role
        return {"user_id": int(user_id), "role": role}
    except JWTError:
        raise credentials_exception
