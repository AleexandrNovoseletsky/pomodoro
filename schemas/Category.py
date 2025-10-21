from typing import Optional

from fastapi.utils import BaseModel


class CreateCategorySchema(BaseModel):
    name: str

class UpdateCategorySchema(BaseModel):
    name: Optional[str] = None

class ResponseCategorySchema(CreateCategorySchema):
    id: int

    class Config:
        from_attributes = True
