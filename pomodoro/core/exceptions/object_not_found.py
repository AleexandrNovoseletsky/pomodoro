"""Ошибки ненахода."""

from fastapi import status

from pomodoro.core.exceptions.base import AppException


class ObjectNotFoundError(AppException):
    """Ошибка – объект в БД не найден."""

    status_code = status.HTTP_404_NOT_FOUND
    error_type = "ObjectNotFoundError"

    def __init__(self, object_id: int):
        """Инициализируем ошибку."""
        super().__init__(
            detail=f"Объект с id={object_id} не найден в базе данных."
        )
