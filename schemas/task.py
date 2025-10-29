from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from settings import Settings

settings = Settings()

name_field_params: dict = {
    "min_length": settings.MIN_TASK_NAME_LENGTH,
    "max_length": settings.MAX_TASK_NAME_LENGTH,
    "description": "название задачи",
}
pomodoro_count_field_params: dict = {
    "ge": settings.MIN_POMODORO_COUNT,
    "le": settings.MAX_POMODORO_COUNT,
}


class CreateTaskSchema(BaseModel):
    name: str = Field(..., **name_field_params)
    pomodoro_count: int = Field(..., **pomodoro_count_field_params)
    category_id: int
    is_active: bool


class CreateTaskORM(CreateTaskSchema):
    author_id: int


class ResponseTaskSchema(CreateTaskSchema):
    id: int
    author_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UpdateTaskSchema(BaseModel):
    name: Optional[str] = Field(None, **name_field_params)
    pomodoro_count: Optional[int] = Field(None, **pomodoro_count_field_params)
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
