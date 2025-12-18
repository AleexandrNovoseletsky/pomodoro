"""Global exception handler for the application.

Provides centralized exception handling for custom application
exceptions. Returns structured JSON responses for AppException and its
subclasses with consistent error formatting and appropriate HTTP status
codes.
"""
from fastapi import status
from fastapi import HTTPException
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


async def http_exception_handler(
        request: Request, exc: HTTPException
) -> JSONResponse:
    """Handle HTTP exceptions with enhanced debugging.

    Temporary implementation with comprehensive debugging output
    to understand exception structure and rate limiting behavior.
    Will be simplified for production use.
    """
    # Comprehensive debug output
    print("\n" + "═" * 70)
    print("🚨 HTTP EXCEPTION DEBUG INFO 🚨")
    print("═" * 70)

    # Exception attributes
    print(f"\n📋 Exception Object:")
    print(f"  Type: {type(exc).__name__}")
    print(f"  Status: {exc.status_code}")
    print(f"  Detail: {exc.detail}")

    # Headers analysis
    print(f"\n📋 Headers Analysis:")
    print(f"  Exception headers: {dict(exc.headers)}")
    print(f"  Request headers keys: {list(request.headers.keys())}")

    # Rate limiting specific
    if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        print(f"\n⚠️  RATE LIMITING DETECTED:")
        all_retry_sources = {
            "exc.headers": exc.headers.get("retry-after"),
            "request.headers": request.headers.get("retry-after"),
        }
        for source, value in all_retry_sources.items():
            print(f"  {source}: {value} (type: {type(value)})")

    print("═" * 70 + "\n")

    # Rate limiting handling (corrected - use exc.headers)
    if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        retry_after = exc.headers.get("Retry-After")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "TooManyRequests",
                "detail": (
                    f"Превышено количество попыток. "
                    f"Повторите через {retry_after} секунд."
                    if retry_after
                    else "Превышено количество попыток. Повторите позже."
                ),
            },
            headers=exc.headers,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )
