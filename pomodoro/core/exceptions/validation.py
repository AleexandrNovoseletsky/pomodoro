"""Input data validation exceptions."""

from fastapi import status
from pydantic import ValidationError

from pomodoro.core.exceptions.base import AppException


class InvalidCreateFileData(AppException):
    """Exception raised when file creation data is invalid."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_type = "InvalidCreateFileData"

    def __init__(
        self, exc: ValidationError | None, detail: str | None = None
    ) -> None:
        """Initialize validation error.

        Args:
            exc: Pydantic ValidationError instance (can be None).
            detail: Custom error detail message.
        """
        formatted = (
            self._format_errors(exc) if exc else "Invalid data provided"
        )
        super().__init__(detail=detail or formatted)

    @staticmethod
    def _format_errors(exc: ValidationError) -> str:
        """Format Pydantic validation errors into readable string.

        Args:
            exc: Pydantic ValidationError.

        Returns:
            Formatted error message.
        """
        errors = exc.errors()
        messages: list[str] = []

        for error in errors:
            field = ".".join(str(loc) for loc in error.get("loc", []))
            msg = error.get("msg", "Invalid value")
            messages.append(f"Ошибка в поле '{field}': {msg}")

        return "; ".join(messages)
