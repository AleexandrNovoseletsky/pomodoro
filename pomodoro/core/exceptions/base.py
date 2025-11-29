"""Basic classes of application errors.

Defines the foundation for custom exception handling throughout the
application. Provides a standardized structure for error responses with
consistent HTTP status codes and error type categorization.
"""

from fastapi import status


class AppException(Exception):
    """Base class for all custom application errors.

    Serves as the foundation for all domain-specific exceptions in the
    application. Provides consistent structure for error handling, HTTP
    status codes, and error response serialization.

    Attributes:     status_code: HTTP status code for the error response
    error_type: Categorized error identifier for client-side handling
    detail: Human-readable error message description
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    error_type: str = "AppException"
    detail: str = "An application error occurred."

    def __init__(self, detail: str | None = None):
        """Initialize application exception.

        Args:     detail: Custom error message for specific error
        scenarios.            If not provided, uses the class default
        message.

        Note:     Custom messages allow for context-specific error
        details while     maintaining consistent exception structure
        across the application.
        """
        if detail:
            self.detail = detail
        super().__init__(self.detail)

    def to_dict(self) -> dict:
        """Convert exception to dictionary.

        Returns:     Dictionary containing error type and detail for
        consistent     error response structure across all API
        endpoints.

        Note:     Used by exception handlers to generate standardized
        error responses     that can be easily consumed by API clients
        and frontend applications.
        """
        return {"error": self.error_type, "detail": self.detail}
