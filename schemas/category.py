from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from settings import Settings

settings = Settings()

name_field_params: dict = {
    "min_length": settings.MIN_CATEGORY_NAME_LENGTH,
    "max_length": settings.MAX_CATEGORY_NAME_LENGTH,
    "description": "название категории",
}


class CreateCategorySchema(BaseModel):
    name: str = Field(..., **name_field_params)
    is_active: bool


class ResponseCategorySchema(CreateCategorySchema):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UpdateCategorySchema(BaseModel):
    name: Optional[str] = Field(None, **name_field_params)
    is_active: Optional[bool] = None
