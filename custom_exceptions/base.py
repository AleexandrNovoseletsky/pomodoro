from fastapi import status


class AppException(Exception):
    """Базовый класс для всех кастомных ошибок проекта."""

    status_code: int = status.HTTP_400_BAD_REQUEST
    error_type: str = "AppException"
    detail: str = "Произошла ошибка приложения."

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)

    def to_dict(self) -> dict:
        return {"error": self.error_type, "detail": self.detail}
