"""Ошибкаи авторизации."""

from fastapi import status

from pomodoro.core.exceptions.base import AppException


class PasswordVerifyError(AppException):
    """Ошибка неверного пароля — возвращается как JSON с 401."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_type = "InvalidCredentials"

    def __init__(self, detail: str | None = None):
        """Инициализируем ошибку."""
        super().__init__(detail or "Неверный логин или пароль.")
