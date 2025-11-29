"""Yandex user schemas.

Defines Pydantic schemas for Yandex OAuth API response data validation
and serialization. Structures user profile information received from
Yandex ID API during OAuth authentication flow.
"""

from datetime import date

from pydantic import BaseModel


class YandexPhone(BaseModel):
    """Phone number data structure received from Yandex OAuth API.

    Represents phone number information provided by Yandex user profile.

    Attributes:     id: Unique identifier for the phone number record
    number: Actual phone number string in Yandex format
    """

    id: int
    number: str


class YandexUserInfo(BaseModel):
    """Complete user profile data received from Yandex OAuth API.

    Validates and structures comprehensive user information provided by
    Yandex ID during OAuth authentication and profile synchronization.

    Attributes:     id: Unique Yandex user identifier (provider_user_id
    in OAuth context)     first_name: User's first name from Yandex
    profile (optional)     last_name: User's last name from Yandex
    profile (optional)     birthday: User's birth date from Yandex
    profile (optional)     default_phone: User's primary phone number
    from Yandex (optional)     default_email: User's primary email
    address from Yandex
    """

    id: str
    first_name: str | None
    last_name: str | None
    birthday: date | None = None
    default_phone: YandexPhone | None = None
    default_email: str
