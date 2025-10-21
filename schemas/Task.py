from typing import Optional

from fastapi.utils import BaseModel


class CreateTaskSchema(BaseModel):
    name: str
    pomodoro_count: int
    category_id: int

class UpdateTaskSchema(BaseModel):
    name: Optional[str] = None
    pomodoro_count: Optional[int] = None
    category_id: Optional[int] = None

class ResponseTaskSchema(CreateTaskSchema):
    id: int

    class Config:
        from_attributes = True

