from fastapi import status

from pomodoro.core.exceptions.base import AppException

class PasswordAlreadySetError(AppException):
    """Password is already set for this user."""

    status_code = status.HTTP_409_CONFLICT
    error_type = "PasswordAlreadySet"
