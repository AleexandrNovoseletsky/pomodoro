"""Ошибки валидации входных данных приложения."""

from fastapi import status
from pydantic import ValidationError

from pomodoro.core.exceptions.base import AppException


class InvalidCreateFileData(AppException):
    """Ошибка — неверные данные при создании записи о файле."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_type = "InvalidCreateFileData"

    def __init__(self, exc: ValidationError, detail: str | None = None):
        """Инициализируем ошибку."""
        formatted = self._format_errors(exc)
        super().__init__(detail=detail or formatted)

    @staticmethod
    def _format_errors(exc: ValidationError) -> str:
        """Форматирование ошибок Pydantic в читаемый вид."""
        errors = exc.errors()

        messages: list[str] = []

        for err in errors:
            field = ".".join(str(x) for x in err.get("loc", []))
            msg = err.get("msg", "Invalid value")
            messages.append(f"Ошибка в поле '{field}': {msg}")

        # Если ошибок несколько — выводим все одной строкой или списком
        return "; ".join(messages)
