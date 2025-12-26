"""Input data validation exceptions.

Defines custom exception classes for data validation failures during
input processing. Provides structured error handling for invalid data
submissions with proper formatting and user-friendly messages.
"""

from fastapi import status
from pydantic import ValidationError

from pomodoro.core.exceptions.base import AppException


class InvalidCreateFileData(AppException):
    """Exception raised when file creation data fails validation.

    Handles validation errors during file upload and creation
    operations, providing detailed field-specific error messages for
    client feedback.

    Attributes:     status_code: HTTP 422 Unprocessable Entity for
    validation failures     error_type: Categorized error type for
    client-side error handling
    """

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_type = "InvalidCreateFileData"

    def __init__(
        self, exc: ValidationError | None, detail: str | None = None
    ) -> None:
        """Initialize file data validation exception with error details.

        Processes Pydantic ValidationError to extract field-specific
        error information and format it into user-readable messages.

        Args:     exc: Pydantic ValidationError instance containing
        validation details     detail: Custom error message to override
        automatic error formatting            (useful for specific
        validation scenarios)

        Note:     If no ValidationError is provided, uses a generic
        invalid data message
        """
        formatted = self.format_errors(exc) if exc else "Invalid data provided"
        super().__init__(detail=detail or formatted)

    @staticmethod
    def format_errors(exc: ValidationError) -> str:
        """Format Pydantic validation errors into human-readable string.

        Extracts field locations and error messages from ValidationError
        and formats them into a structured, user-friendly error message.

        Args:     exc: Pydantic ValidationError containing validation
        failure details

        Returns:     Formatted error message string with field-specific
        error descriptions

        Note:     Handles nested field structures by joining location
        paths with dots     to create comprehensive field identifiers
        """
        errors = exc.errors()
        messages: list[str] = []

        for error in errors:
            field = ".".join(str(loc) for loc in error.get("loc", []))
            msg = error.get("msg", "Invalid value")
            messages.append(f"Error in field '{field}': {msg}")

        return "; ".join(messages)

class InvalidImageFile(AppException):
    """Exception raised when uploaded file is not a valid image.

    Used when file content cannot be identified as an image or when
    image decoding fails at early validation stages.
    """

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_type = "InvalidImageFile"

    def __init__(self, filename: str | None = None) -> None:
        """Initialize invalid image exception.

        Args:
            filename: Optional original filename for better diagnostics
        """
        detail = (
            f"Файл '{filename}' не является допустимым изображением"
            if filename
            else "Переданный файл не является допустимым изображением"
        )
        super().__init__(detail=detail)
