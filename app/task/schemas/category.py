from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.core.settings import Settings
from app.task.schemas.task import name_field

settings = Settings()

name_field_params: dict = {
    "min_length": settings.MIN_CATEGORY_NAME_LENGTH,
    "max_length": settings.MAX_CATEGORY_NAME_LENGTH,
    "description": "название категории",
}


class CreateCategorySchema(BaseModel):
    name: str = name_field(...)
    is_active: bool


class ResponseCategorySchema(CreateCategorySchema):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateCategorySchema(BaseModel):
    name: Optional[str] = name_field(None)
    is_active: Optional[bool] = None
