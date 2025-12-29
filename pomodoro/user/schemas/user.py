"""User schemas.

Defines Pydantic schemas for user data validation, serialization, and
API communication. Includes schemas for creation, database operations,
response, and update operations with proper field constraints and
validation rules for user profile management.
"""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from pomodoro.auth.exceptions.password_incorrect import PasswordVerifyError
from pomodoro.core.settings import Settings
from pomodoro.core.validators.password import password_field_validator
from pomodoro.user.models.users import UserRole

settings = Settings()


def name_field(default: Any):
    """Field constraints for user's name length validation.

    Args:
        default: Default value for the field

    Returns:
        Field configuration with length constraints and
        description
    """
    return Field(
        default,
        min_length=settings.MIN_USER_NAME_LENGTH,
        max_length=settings.MAX_USER_NAME_LENGTH,
        description="User first name, last name or middle name",
    )


class BaseUserProfileSchema(BaseModel):
    """Base schema for user profile data with common fields.

    Defines common user profile fields with validation constraints used
    across multiple operation types.

    Attributes:
        phone: Normalized phone number in +7 format
        first_name: User's first name with length validation
        last_name: User's last name with length validation
        patronymic: User's patronymic/middle name
                    with length validation
        birthday: User's date of birth
        email: User's email address with length validation
        about: User biography or description
               with length validation
    """

    phone: str | None = Field(
        None, min_length=12, max_length=12, description="+7 999 999 99 99"
    )
    first_name: str | None = name_field(None)
    last_name: str | None = name_field(None)
    patronymic: str | None = name_field(None)

    birthday: date | None = None
    email: str | None = Field(None, max_length=settings.MAX_EMAIL_LENGTH)

    about: str | None = Field(
        None,
        max_length=settings.MAX_USER_ABOUT_LENGTH,
        description="About the user",
    )


class CreateUserProfileSchema(BaseUserProfileSchema):
    """Schema for user creation with user-provided data.

    Extends base schema with password field for initial user
    registration.

    Attributes:
        password: Plain text password for initial
                  authentication setup
    """

    password: str | None = Field(None, min_length=settings.MIN_PASSWORD_LENGTH)

    _validate_password = password_field_validator("password")


class CreateUserProfileORM(BaseUserProfileSchema):
    """Schema for user creation in database operations.

    Extends base schema with hashed password for secure database
    storage. Used internally for database operations after password
    hashing.

    Attributes:
        hashed_password: Securely hashed password for
        database storage
    """

    hashed_password: str


class ResponseUserProfileSchema(BaseUserProfileSchema):
    """Schema for user response data with complete profile information.

    Extends base schema with system-generated fields and verification
    status for complete user representation in API responses.

    Attributes:
        id: System-generated user identifier
        phone_verified: Current phone number verification status
        patronymic: User's patronymic/middle name
        birthday: User's date of birth
        created_at: Timestamp of user registration
        updated_at: Timestamp of last profile modification
        email: User's email address
        email_verified: Current email verification status
        about: User biography or description
        is_active: Current account active status
        role: User role for access control
    """

    id: int
    phone_verified: bool
    patronymic: str | None
    birthday: date | None
    created_at: datetime
    updated_at: datetime
    email: str | None
    email_verified: bool
    about: str | None
    is_active: bool
    role: UserRole

    model_config = {"from_attributes": True}


class UpdateUserProfileSchema(BaseUserProfileSchema):
    """Schema for user profile updates with partial data support.

    Extends base schema with optional email verification field for
    administrative updates. All fields are optional for partial updates.

    Attributes:
        email_verified: Optional email verification status update
    """

    email_verified: bool | None = None


class SetPasswordSchema(BaseModel):
    """Schema for set or set user password.

    Attributes:
        new_password: New user password
    """
    new_password: str

    _validate_password = password_field_validator(
        field_name="new_password"
    )


class ChangePasswordSchema(SetPasswordSchema):
    """Schema for change user password.

    Attributes:
        old_password: Old user password
    """
    old_password: str

    @model_validator(mode='after')
    def check_passwords_differ(self) -> 'ChangePasswordSchema':
        """Validate that new password differs from old password."""
        if self.new_password == self.old_password:
            raise PasswordVerifyError(
                detail='New password must be different from the old one'
            )
        return self

class UpdatePasswordORMSchema(BaseModel):
    """Schemas for update password in BD.

    Attributes:
        hashed_password: Securely hashed password for
        database storage
    """
    hashed_password: str


class ResetPasswordSchema(BaseModel):
    """Schema for reset password.

    Attributes:
        phone: user phone
    """
    phone: str


class CheckRecoveryCodeSchema(BaseModel):
    """Schema for check recovery password code.

    Attributes:
        recovery_id: ID recovery session
        recovery_code: Password reset code sent to the user

    """
    recovery_id: str
    recovery_code: int


class ConfirmResetPasswordSchema(SetPasswordSchema):
    """Schema for confirm reset password via recovery token.

    Attributes:
        token: Password recovery token
        new_password: New user password
    """
    token: str
