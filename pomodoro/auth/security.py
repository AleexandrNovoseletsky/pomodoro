"""Утилиты для хеширования паролей и создания JWT-токенов.

Модуль обеспечивает функции для верификации и генерации паролей,
а также для создания токенов доступа (JWT).
"""


from datetime import UTC, datetime

from jose import jwt
from passlib.context import CryptContext

from pomodoro.core.settings import Settings

settings = Settings()

pwd_context = CryptContext(
    schemes=[settings.CRYPTO_CONTEXT], deprecated="auto"
)


def verify_password(plain_password, hashed_password) -> bool:
    """Прверка пароля."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    """Гкнирация хэш-пароля."""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Гкнирация токена."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + settings.JWT_LIFE_SPAN
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt
