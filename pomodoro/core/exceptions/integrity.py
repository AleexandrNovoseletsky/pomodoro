"""Ошибки целостности базы данных."""

from fastapi import status
from sqlalchemy.exc import IntegrityError

from pomodoro.core.exceptions.base import AppException


class IntegrityDBError(AppException):
    """Ошибки целостности базы данных."""

    status_code = status.HTTP_409_CONFLICT
    error_type = "IntegrityDBError"

    def __init__(self, exc: IntegrityError):
        """Инициализируем ошибку."""
        error_message = str(exc.orig).lower()

        # Определяем тип ошибки по сообщению БД
        if "unique constraint" in error_message:
            detail = "Объект с таким уникальным значением уже существует."
        elif "duplicate key value" in error_message:
            detail = "Объект с таким уникальным ключом уже существует."
        elif "not-null constraint" in error_message:
            detail = "Одно из обязательных полей не может быть пустым."
        elif "foreign key constraint" in error_message:
            detail = "Ссылка на несуществующую запись. Проверьте foreign key."
        else:
            detail = "Ошибка целостности базы данных."

        # Передаём в базовый класс человеко-понятное сообщение
        super().__init__(detail=detail)

        # Добавляем оригинальное SQL-сообщение для отладки
        self.db_error = error_message

    def to_dict(self) -> dict:
        """Расширяем базовый to_dict, чтобы добавить SQL-ошибку."""
        base = super().to_dict()
        base["db_error"] = self.db_error
        return base
