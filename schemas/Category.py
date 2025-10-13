from fastapi.utils import BaseModel


class CreateCategory(BaseModel):
    name: str

class ResponseCategory(CreateCategory):
    id: int
