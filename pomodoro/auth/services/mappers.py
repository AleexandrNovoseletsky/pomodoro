"""Authentication mappers.

Provides data transformation utilities for converting external OAuth
provider data to application-specific schemas. Handles data
normalization and mapping between different data formats and structures.
"""

from pomodoro.auth.schemas.oauth import OAuthCreateSchema
from pomodoro.auth.schemas.yandex_user import YandexUserInfo
from pomodoro.core.utils.normalize import normalize_name, normalize_phone
from pomodoro.user.schemas.user import CreateUserProfileSchema


def yandex_to_user_and_oauth(
    data: YandexUserInfo,
) -> tuple[CreateUserProfileSchema, OAuthCreateSchema]:
    """Transform Yandex OAuth user data to application schemas.

    Converts raw user profile data received from Yandex OAuth API into
    structured application schemas for user creation and OAuth account
    linking. Applies data normalization for consistency and validation.

    Args:     data: Complete user profile data received from Yandex
    OAuth API

    Returns:     Tuple containing:     - CreateUserProfileSchema: User
    profile data for registration/update     - OAuthCreateSchema: OAuth
    account data for provider linking

    Note:     Applies phone number normalization and name capitalization
    to ensure data consistency across the application
    """
    # Normalize phone number from Yandex format to application standard
    phone = None
    if data.default_phone is not None:
        phone = normalize_phone(data.default_phone.number)

    # Create user profile schema with normalized data
    user = CreateUserProfileSchema(
        phone=phone,
        first_name=normalize_name(data.first_name),
        last_name=normalize_name(data.last_name),
        birthday=data.birthday,
        email=data.default_email,
        patronymic=None,
        about=None,
        password=None,
    )

    # Create OAuth account schema for provider linking
    oauth = OAuthCreateSchema(
        provider="yandex",
        provider_user_id=data.id,
        phone=phone,
        first_name=normalize_name(data.first_name),
        last_name=normalize_name(data.last_name),
        birthday=data.birthday,
        email=data.default_email,
    )

    return user, oauth
