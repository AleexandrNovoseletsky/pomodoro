"""Схема пользователя от Янжекса."""

from datetime import date

from pydantic import BaseModel


class YandexPhone(BaseModel):
    """Телефон пользователя, полученный от яндекса."""

    id: int
    number: str


class YandexUserInfo(BaseModel):
    """Схема пользователя от Яндекса."""

    id: str
    first_name: str | None
    last_name: str | None
    access_token: str
    birthday: date | None = None
    default_phone: YandexPhone | None = None
    default_email: str
