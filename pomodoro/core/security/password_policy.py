"""Password policy validation utilities."""

import re

from pomodoro.auth.exceptions.password_incorrect import PasswordVerifyError


class PasswordPolicy:
    """Password complexity validation rules."""

    @staticmethod
    def validate(value: str) -> None:
        """Validate password complexity.

        Raises:
            ValueError: If password does not meet complexity requirements
        """
        if not re.search(r"[a-z]", value):
            raise PasswordVerifyError(
                detail=("Password must contain at "
                        "least one lowercase letter")
            )

        if not re.search(r"[A-Z]", value):
            raise PasswordVerifyError(
                detail=("Password must contain at "
                 "least one uppercase letter")
            )

        if not re.search(r"\d", value):
            raise PasswordVerifyError(
                detail=("Password must contain "
                        "at least one digit")
            )

        if not re.search(r"[^\w\s]", value):
            raise PasswordVerifyError(
                detail=("Password must contain at "
                        "least one special character")
            )
