from datetime import datetime, UTC

from jose import jwt
from passlib.context import CryptContext

from app.core.settings import Settings

settings = Settings()

pwd_context = CryptContext(
    schemes=[settings.CRYPTO_CONTEXT], deprecated="auto"
)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + settings.JWT_LIFE_SPAN
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt
