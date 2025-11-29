"""Database integrity errors.

Defines custom exception classes for database integrity constraint
violations. Provides user-friendly error messages for common database
constraint failures while preserving technical details for debugging
purposes.
"""

from fastapi import status
from sqlalchemy.exc import IntegrityError

from pomodoro.core.exceptions.base import AppException


class IntegrityDBError(AppException):
    """Exception raised for database integrity constraint violations.

    Handles SQLAlchemy IntegrityError exceptions and converts them into
    user-friendly error messages while preserving technical details for
    development and debugging purposes.

    Attributes:     status_code: HTTP 409 Conflict status code for
    constraint violations     error_type: Categorized error type for
    client-side error handling     db_error: Original database error
    message for technical reference
    """

    status_code = status.HTTP_409_CONFLICT
    error_type = "IntegrityDBError"

    def __init__(self, exc: IntegrityError):
        """Initialize integrity error.

        Analyzes the original SQLAlchemy IntegrityError to determine the
        specific type of constraint violation and generate appropriate
        user-facing messages.

        Args:     exc: Original SQLAlchemy IntegrityError containing
        database constraint details

        Note:     Preserves original database error message in db_error
        attribute     for debugging while providing user-friendly
        messages in the detail
        """
        error_message = str(exc.orig).lower()

        # Determine error type by analyzing original database error message
        if "unique constraint" in error_message:
            detail = "Object with this unique value already exists."
        elif "duplicate key value" in error_message:
            detail = "Object with this unique key already exists."
        elif "not-null constraint" in error_message:
            detail = "One of the required fields cannot be empty."
        elif "foreign key constraint" in error_message:
            detail = ("Reference to non-existent record. "
                      "Please check foreign key relationships.")
        else:
            detail = "Database integrity constraint violation."

        # Pass human-readable message to base class
        super().__init__(detail=detail)

        # Preserve original SQL error message for technical reference
        self.db_error = error_message

    def to_dict(self) -> dict:
        """Extend base serialization method to include details.

        Returns:     Dictionary containing error type, user-friendly
        detail,     and technical database error information for
        debugging

        Note:     Database error details are included for development
        and     debugging purposes but could be filtered in production
        environments for security
        """
        base = super().to_dict()
        base["db_error"] = self.db_error
        return base
