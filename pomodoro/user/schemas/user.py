"""Схемы пользователей."""

from datetime import date, datetime

from pydantic import BaseModel, Field

from pomodoro.core.settings import Settings
from pomodoro.task.schemas.task import name_field
from pomodoro.user.models.users import UserRole

settings = Settings()

# Ограничения длинны для ФИО
name_field_params: dict = {
    "min_length": settings.MIN_USER_NAME_LENGTH,
    "max_length": settings.MAX_USER_NAME_LENGTH,
    "description": "имя, фамилия, или отчество пользователя",
}


class BaseUserProfileSchema(BaseModel):
    """Базоавая схема пользователя."""

    phone: str | None = Field(
        None, min_length=12, max_length=12, description="+7 999 999 99 99"
    )
    first_name: str | None = name_field(None)
    last_name: str | None = name_field(None)
    patronymic: str | None = Field(
        None,
        min_length=settings.MIN_USER_NAME_LENGTH,
        max_length=settings.MAX_USER_NAME_LENGTH,
        description="отчество",
    )

    birthday: date | None = None
    email: str | None = Field(None, max_length=settings.MAX_EMAIL_LENGTH)

    about: str | None = Field(
        None,
        max_length=settings.MAX_USER_ABOUT_LENGTH,
        description="о пользователе",
    )


class CreateUserProfileSchema(BaseUserProfileSchema):
    """Принимаемые от пользователя данные для создания пользователя."""

    password: str | None = Field(
        None, min_length=settings.MIN_PASSWORD_LENGTH
    )


class CreateUserProfileORM(BaseUserProfileSchema):
    """Данные для создания пользователя в БД."""

    hashed_password: str


class ResponseUserProfileSchema(BaseUserProfileSchema):
    """Возвращаемые пользователю данные."""

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
    """Данные для обновления данных о пользователе."""

    pass
