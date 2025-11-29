"""Access Exceptions.

Defines custom exception classes for authorization and access control
error scenarios. Provides structured error handling for permission
failures with proper HTTP status codes and user-friendly error messages.
"""

from fastapi import status

from pomodoro.core.exceptions.base import AppException


class AccessDenied(AppException):
    """Exception raised when user lacks required permissions.

    This exception is used when authenticated users attempt to perform
    actions beyond their authorization level, such as accessing admin
    resources or modifying other users' data without proper privileges.

    Attributes:     status_code: HTTP 403 Forbidden status code for
    authorization failures     error_type: Categorized error type for
    client-side error handling
    """

    status_code = status.HTTP_403_FORBIDDEN
    error_type = "AccessDenied"

    def __init__(self, detail: str | None = None):
        """Initialize access denied exception with customizable message.

        Args:     detail: Custom error message for specific
        authorization failure scenarios.            Uses generic access
        denied message if not provided to maintain            consistent
        user experience across authorization failures.

        Note:     Generic error messaging is used for security to avoid
        revealing     unnecessary information about system resources and
        permissions structure.
        """
        super().__init__(
            detail=detail
            or "You do not have permission to perform this action."
        )
