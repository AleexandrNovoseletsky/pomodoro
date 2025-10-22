from typing import Optional

from pydantic import BaseModel, Field, field_validator

from settings import Settings


settings = Settings()
validator_params: dict = {
    'min_length': settings.MIN_CATEGORY_NAME_LENGTH,
    'max_length': settings.MAX_CATEGORY_NAME_LENGTH,
    'field_name': 'название категории'
}
name_field_params = validator_params.copy()
name_field_params['description'] = name_field_params.pop('field_name')

class CreateCategorySchema(BaseModel):
    name: str = Field(..., **name_field_params)

class UpdateCategorySchema(BaseModel):
    name: Optional[str] = Field(
        None,
        ** name_field_params
    )

class ResponseCategorySchema(CreateCategorySchema):
    id: int

    class Config:
        from_attributes = True
