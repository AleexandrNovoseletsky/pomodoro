"""Global exception handler for the application.

Provides centralized exception handling for custom application
exceptions. Returns structured JSON responses for AppException and its
subclasses with consistent error formatting and appropriate HTTP status
codes.
"""

from starlette.requests import Request
from starlette.responses import JSONResponse

from pomodoro.core.exceptions.base import AppException


async def app_exception_handler(
    request: Request, exc: AppException
) -> JSONResponse:
    """Handle application exceptions.

    Intercepts AppException and its subclasses to provide consistent
    error response formatting across all API endpoints. Converts
    application exceptions to standardized JSON responses with
    appropriate HTTP status codes and error details.

    Args:     request: The incoming HTTP request that triggered the
    exception     exc: The AppException instance containing error
    details

    Returns:     JSONResponse with standardized error format including:
    - HTTP status code from the exception     - Error type identifier
    for client-side handling     - Human-readable error message detail

    Note:     This handler ensures all custom application exceptions
    return     consistent JSON structure regardless of where they occur
    in     the application stack
    """
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())
