from fastapi.utils import BaseModel


class CreateTaskSchema(BaseModel):
    name: str
    pomodoro_count: int
    category_id: int

class ResponseTaskSchema(CreateTaskSchema):
    id: int

    class Config:
        from_attributes = True

