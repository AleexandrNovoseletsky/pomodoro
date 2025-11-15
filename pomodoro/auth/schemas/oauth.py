"""Схемы авторизации."""

from datetime import date

from pydantic import BaseModel


class OAuthCreateSchema(BaseModel):
    """Данные от внешнего провайдера авторизации."""

    provider: str
    provider_user_id: str
    first_name: str | None
    last_name: str | None
    access_token: str
    birthday: date | None = None
    phone: str | None = None
    email: str


class OAuthCreateORM(OAuthCreateSchema):
    """Данные пользователя для записи в БД."""

    user_id: int
