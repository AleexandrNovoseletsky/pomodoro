from pydantic import field_validator

from pomodoro.core.security.password_policy import PasswordPolicy


def password_field_validator(field_name: str):
    """Create reusable password field validator."""

    def _validator(cls, value: str | None) -> str | None:
        if value is None:
            return value

        PasswordPolicy.validate(value)
        return value

    return field_validator(field_name)(_validator)
