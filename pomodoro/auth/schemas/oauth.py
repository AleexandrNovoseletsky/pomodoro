"""Authentication schemas.

Defines Pydantic schemas for OAuth authentication data validation and
serialization. Includes schemas for OAuth provider data, database
operations, and access token responses.
"""

from datetime import date

from pydantic import BaseModel


class OAuthCreateSchema(BaseModel):
    """Schema for OAuth provider data.

    Validates and structures user profile information received from
    OAuth providers such as Yandex, Google, etc. during the
    authentication flow.

    Attributes:     provider: OAuth provider name (e.g., 'yandex',
    'google')     provider_user_id: Unique user identifier from the
    OAuth provider     first_name: User's first name from OAuth provider
    (optional)     last_name: User's last name from OAuth provider
    (optional)     birthday: User's birth date from OAuth provider
    (optional)     phone: User's phone number from OAuth provider
    (optional)     email: User's email address from OAuth provider
    """

    provider: str
    provider_user_id: str
    first_name: str | None
    last_name: str | None
    birthday: date | None = None
    phone: str | None = None
    email: str


class OAuthCreateORM(OAuthCreateSchema):
    """Schema for OAuth account creation in database operations.

    Extends OAuth provider data with system-generated user identifier
    for creating the relationship between OAuth accounts and local
    users.

    Attributes:     user_id: System-generated identifier of the
    associated user profile
    """

    user_id: int


class AccessTokenSchema(BaseModel):
    """Schema for JWT access token responses.

    Standardized response format for authentication endpoints that
    return access tokens for API authorization.

    Attributes:     access_token: JWT token string for API
    authentication     token_type: Token type identifier (default:
    'bearer' for Bearer token authentication)
    """

    access_token: str
    token_type: str = "bearer"
