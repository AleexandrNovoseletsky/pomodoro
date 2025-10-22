from typing import Optional

from pydantic import BaseModel, Field, field_validator

from settings import Settings


settings = Settings()

validator_params: dict = {
    'min_length': settings.MIN_TASK_NAME_LENGTH,
    'max_length': settings.MAX_TASK_NAME_LENGTH,
    'field_name': 'название задачи',
}
name_field_params = validator_params.copy()
name_field_params['description'] = name_field_params.pop('field_name')
pomodoro_count_field_params: dict = {
    'ge': settings.MIN_POMODORO_COUNT,
    'le': settings.MAX_POMODORO_COUNT,
}

class CreateTaskSchema(BaseModel):
    name: str = Field(..., **name_field_params)
    pomodoro_count: int = Field(..., **pomodoro_count_field_params)
    category_id: int

class UpdateTaskSchema(BaseModel):
    name: Optional[str] = Field(None, **name_field_params)
    pomodoro_count: Optional[int] = Field(
        None,
        **pomodoro_count_field_params
    )
    category_id: Optional[int] = None

class ResponseTaskSchema(CreateTaskSchema):
    id: int

    class Config:
        from_attributes = True

