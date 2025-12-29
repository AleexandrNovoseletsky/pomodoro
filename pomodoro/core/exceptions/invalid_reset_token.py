"""Invalid reset token exception."""

from fastapi import status

from pomodoro.core.exceptions.base import AppException


class InvalidResetToken(AppException):
    """Invalid reset password token."""

    status_code = status.HTTP_403_FORBIDDEN
    error_type = "InvalidResetToken"
