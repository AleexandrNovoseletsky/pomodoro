from starlette.requests import Request
from starlette.responses import JSONResponse

from custom_exceptions.base import AppException


async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


async def default_exception_handler(request: Request, exc: Exception):
    """Фолбэк для непредвиденных ошибок."""
    return JSONResponse(
        status_code=500,
        content={"error": exc.__class__.__name__, "detail": str(exc)},
    )
