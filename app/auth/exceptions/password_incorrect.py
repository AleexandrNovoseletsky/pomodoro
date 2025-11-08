from fastapi import status

from app.core.exceptions.base import AppException


class PasswordVerifyError(AppException):
    """Ошибка неверного пароля — возвращается как JSON с 401."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_type = "InvalidCredentials"

    def __init__(self, detail: str | None = None):
        # Сообщение по-умолчанию даёт понятный текст для API-пользователя
        super().__init__(detail or "Неверный логин или пароль.")
