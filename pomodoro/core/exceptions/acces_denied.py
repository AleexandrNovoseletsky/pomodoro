"""Ошибки парв доступа."""

from fastapi import status

from pomodoro.core.exceptions.base import AppException


class AccessDenied(AppException):
    """Ошибка парв доступа."""

    status_code = status.HTTP_403_FORBIDDEN
    error_type = "AccessDenied"

    def __init__(self, message: str | None = None):
        """Инициализируем ошибку."""
        super().__init__(
            detail=message or "У вас нет прав для выполнения этого действия."
        )
