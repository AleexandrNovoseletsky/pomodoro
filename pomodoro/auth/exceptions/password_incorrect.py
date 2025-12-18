"""Authorization errors.

Defines custom exception classes for authentication and authorization
error scenarios. Provides structured error handling for authentication
failures with proper HTTP status codes and error type categorization.
"""

from fastapi import status

from pomodoro.core.exceptions.base import AppException


class PasswordVerifyError(AppException):
    """Exception raised when password verification fails.

    This exception is used when provided credentials (password) do not
    match the stored credentials for a user during login attempts.

    Attributes:     status_code: HTTP 401 Unauthorized status code for
    authentication failures     error_type: Categorized error type for
    client-side error handling
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    error_type = "InvalidCredentials"

    def __init__(self, detail: str | None = None):
        """Initialize password verification error.

        Args:
            detail: Custom error message for specific
                    authentication failure scenarios.
                    Uses generic
                    "Invalid login or password"
                    message if not provided
                    to avoid revealing whether username
                    or password was incorrect.

        Note:
            Generic error messaging is used for security to
            prevent user enumeration attacks that could determine which
            usernames exist in the system.
        """
        super().__init__(detail or "Неверный логин или пароль.")
