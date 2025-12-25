"""Not found exceptions.

Defines custom exception classes for resource not found scenarios.
Provides structured error handling for missing resources with proper
HTTP status codes and informative error messages.
"""

from fastapi import status

from pomodoro.core.exceptions.base import AppException


class ObjectNotFoundError(AppException):
    """Exception raised when a requested resource cannot be found.

    This exception is used when operations attempt to access or modify
    resources that don't exist in the system, such as non-existent
    users, tasks, or categories.

    Attributes:     status_code: HTTP 404 Not Found status code for
    missing resources     error_type: Categorized error type for client-
    side error handling
    """

    status_code = status.HTTP_404_NOT_FOUND
    error_type = "ObjectNotFoundError"

    def __init__(self, object_id: int):
        """Initialize object not found exception.

        Args:
            object_id: Unique identifier of the resource that
                        could not be found

        Note:
            Includes the specific object ID in the error message
            to help clients identify which resource was not found while
            maintaining consistent error response structure
        """
        super().__init__(
            detail=f"Object with id={object_id} was not found in the database."
        )
