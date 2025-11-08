from fastapi import status

from app.core.exceptions.base import AppException


class ObjectNotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    error_type = "ObjectNotFoundError"

    def __init__(self, object_id: int):
        super().__init__(
            detail=f"Объект с id={object_id} не найден в базе данных."
        )
