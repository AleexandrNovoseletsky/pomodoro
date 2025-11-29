"""User not found errors.

Defines custom exception classes for user-related error scenarios.
Provides structured error handling for user lookup failures with proper
context and messaging.
"""


class UserNotFoundError(Exception):
    """Exception raised when user cannot be found in the system.

    This exception is used when user lookup operations fail due to non-
    existent users, typically during authentication or profile
    retrieval.

    Attributes:     phone: Phone number that was used for the lookup
    attempt (optional)
    """

    def __init__(self, phone: str | None = None):
        """Initialize user not found error with optional phone context.

        Args:     phone: Phone number that was used in the lookup
        attempt
        """
        self.phone = phone

    def __str__(self):
        """String representation of the error for logging and display.

        Returns:     Formatted error message with phone context if
        available
        """
        return f"User {self.phone} not found."
