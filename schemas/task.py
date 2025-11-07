from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from settings import Settings

settings = Settings()


def name_field(default: Any):
    return Field(default,
                 min_length=settings.MIN_TASK_NAME_LENGTH,
                 max_length=settings.MAX_TASK_NAME_LENGTH,
                 description="название задачи"
                 )


def p_count_field(default: Any):
    return Field(default,
                 ge=settings.MIN_POMODORO_COUNT,
                 le=settings.MAX_POMODORO_COUNT
                 )


class CreateTaskSchema(BaseModel):
    name: str = name_field(...)
    pomodoro_count: int = p_count_field(...)
    category_id: int
    is_active: bool


class CreateTaskORM(CreateTaskSchema):
    author_id: int


class ResponseTaskSchema(CreateTaskSchema):
    id: int
    author_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateTaskSchema(BaseModel):
    name: Optional[str] = name_field(None)
    pomodoro_count: Optional[int] = p_count_field(None)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
