"""Схемы задач."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from pomodoro.core.settings import Settings

settings = Settings()


def name_field(default: Any):
    """Ограничения длинны ФИО."""
    return Field(
        default,
        min_length=settings.MIN_TASK_NAME_LENGTH,
        max_length=settings.MAX_TASK_NAME_LENGTH,
        description="название задачи",
    )


def pomodoro_count_field(default: Any):
    """Огнаничение продолжительности времени по задаче."""
    return Field(
        default, ge=settings.MIN_POMODORO_COUNT, le=settings.MAX_POMODORO_COUNT
    )


class CreateTaskSchema(BaseModel):
    """Принимаемые от пользователя данные для создания задачи."""

    name: str = name_field(...)
    pomodoro_count: int = pomodoro_count_field(...)
    category_id: int
    is_active: bool | None = None


class CreateTaskORM(CreateTaskSchema):
    """Данные для создания задачи в БД."""

    author_id: int


class ResponseTaskSchema(CreateTaskSchema):
    """Возвращаемые пользователю данные по задаче."""

    id: int
    author_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateTaskSchema(BaseModel):
    """Данные для изминения задачи."""

    name: str | None = name_field(None)
    pomodoro_count: int | None = pomodoro_count_field(None)
    category_id: int | None = None
    is_active: bool | None = None
