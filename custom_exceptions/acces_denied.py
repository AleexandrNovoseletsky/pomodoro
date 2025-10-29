from fastapi import status

from custom_exceptions.base import AppException


class AccessDenied(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    error_type = "AccessDenied"

    def __init__(self, message: str | None = None):
        super().__init__(
            detail=message or "У вас нет прав для выполнения этого действия."
        )
