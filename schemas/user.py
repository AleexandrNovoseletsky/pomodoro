from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field

from models.users import UserRole
from settings import Settings

settings = Settings()

name_field_params: dict = {
    'min_length': settings.MIN_USER_NAME_LENGTH,
    'max_length': settings.MAX_USER_NAME_LENGTH,
    'description': 'имя, фамилия, или отчество пользователя',
}


class BaseUserSchema(BaseModel):
    phone: str = Field(
        ...,
        min_length=12,
        max_length=12,
        description='+7 999 999 99 99'
    )

    first_name: str = Field(..., **name_field_params)
    last_name: str = Field(..., **name_field_params)


class CreateUserSchema(BaseUserSchema):
    password: str = Field(..., min_length=settings.MIN_PASSWORD_LENGTH)


class CreateUserORM(BaseUserSchema):
    hashed_password: str


class ResponseUserSchema(CreateUserORM):
    id: int
    phone_verified: bool
    patronymic: str | None
    birthday: date | None
    created_at: datetime
    email: str | None
    email_verified: bool
    hashed_password: str
    photo_path: str | None
    about: str | None
    is_active: bool
    role: UserRole

    class Config:
        from_attributes = True


class UpdateUserSchema(BaseModel):
    phone: Optional[str] = Field(
        None,
        min_length=12,
        max_length=12,
        description='+7 999 999 99 99'
    )

    patronymic: Optional[str] = Field(
        None,
        min_length=settings.MIN_USER_NAME_LENGTH,
        max_length=settings.MAX_USER_NAME_LENGTH,
        description='отчество'
    )

    birthday: Optional[date]
    email: Optional[str] = Field(
        None,
        max_length=settings.MAX_EMAIL_LENGTH
    )

    about: Optional[str] = Field(
        None,
        max_length=settings.MAX_USER_ABOUT_LENGTH,
        description='о пользователе'
    )


class LoginUserSchema(BaseModel):
    phone: str
    password: str
