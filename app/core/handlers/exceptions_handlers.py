"""Глобальный обработчик исключений для приложения.

Возвращает структурированный JSON для `AppException` и общий
ответ для остальных ошибок с кодом 500.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.exceptions.base import AppException


async def app_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Обработать исключение приложения и вернуть JSONResponse.

    При получении AppException возвращаем её код и словарь через
    метод `to_dict()`. Для прочих исключений возвращаем минимальный
    ответ с кодом 500 и названием исключения.
    """
    if isinstance(exc, AppException):
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    return JSONResponse(
        status_code=500,
        content={"error": exc.__class__.__name__, "detail": str(exc)},
    )
