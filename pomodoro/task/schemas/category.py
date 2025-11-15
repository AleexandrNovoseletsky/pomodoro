"""Схемы категорий."""

from datetime import datetime

from pydantic import BaseModel

from pomodoro.core.settings import Settings
from pomodoro.task.schemas.task import name_field

settings = Settings()

# Ограничения длинны названия
name_field_params: dict = {
    "min_length": settings.MIN_CATEGORY_NAME_LENGTH,
    "max_length": settings.MAX_CATEGORY_NAME_LENGTH,
    "description": "название категории",
}


class CreateCategorySchema(BaseModel):
    """принимаемые от пользователя поля для создании категории."""

    name: str = name_field(...)
    is_active: bool | None = None


class ResponseCategorySchema(CreateCategorySchema):
    """Схема категорий для ответа пользователю."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateCategorySchema(BaseModel):
    """принимаемые от пользователя поля для изминения категории."""

    name: str | None = name_field(None)
    is_active: bool | None = None
