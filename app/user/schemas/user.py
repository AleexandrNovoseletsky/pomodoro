from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, Field

from app.user.models.users import UserRole
from app.task.schemas.task import name_field
from app.core.settings import Settings

settings = Settings()

name_field_params: dict = {
    "min_length": settings.MIN_USER_NAME_LENGTH,
    "max_length": settings.MAX_USER_NAME_LENGTH,
    "description": "имя, фамилия, или отчество пользователя",
}


class BaseUserProfileSchema(BaseModel):
    phone: Optional[str] = Field(
        None, min_length=12, max_length=12, description="+79999999999"
    )

    first_name: Optional[str] = name_field(None)
    last_name: Optional[str] = name_field(None)
    patronymic: Optional[str] = name_field(None)
    birthday: Optional[date] = None
    email: Optional[str] = Field(None, max_length=settings.MAX_EMAIL_LENGTH)
    about: Optional[str] = Field(
        None,
        max_length=settings.MAX_USER_ABOUT_LENGTH,
        description="о пользователе",
    )


class CreateUserProfileSchema(BaseUserProfileSchema):
    password: Optional[str] = Field(
        None, min_length=settings.MIN_PASSWORD_LENGTH
        )


class CreateUserProfileORM(BaseUserProfileSchema):
    hashed_password: str


class ResponseUserProfileSchema(CreateUserProfileORM):
    id: int
    phone_verified: bool
    patronymic: str | None
    birthday: date | None
    created_at: datetime
    updated_at: datetime
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
        None, min_length=12, max_length=12, description="+7 999 999 99 99"
    )
    first_name: Optional[str] = name_field(None)
    last_name: Optional[str] = name_field(None)
    patronymic: Optional[str] = Field(
        None,
        min_length=settings.MIN_USER_NAME_LENGTH,
        max_length=settings.MAX_USER_NAME_LENGTH,
        description="отчество",
    )

    birthday: Optional[date]
    email: Optional[str] = Field(None, max_length=settings.MAX_EMAIL_LENGTH)

    about: Optional[str] = Field(
        None,
        max_length=settings.MAX_USER_ABOUT_LENGTH,
        description="о пользователе",
    )


class LoginUserSchema(BaseModel):
    phone: str
    password: str
