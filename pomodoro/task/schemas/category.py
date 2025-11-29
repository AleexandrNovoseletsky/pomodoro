"""Category schemas.

Defines Pydantic schemas for category data validation, serialization,
and API communication. Includes schemas for creation, response, and
update operations with proper field constraints.
"""

from datetime import datetime

from pydantic import BaseModel

from pomodoro.core.settings import Settings
from pomodoro.task.schemas.task import name_field

settings = Settings()

# Field length constraints for category names
name_field_params: dict = {
    "min_length": settings.MIN_CATEGORY_NAME_LENGTH,
    "max_length": settings.MAX_CATEGORY_NAME_LENGTH,
    "description": "Category name",
}


class CreateCategorySchema(BaseModel):
    """Schema for category creation with user-provided data.

    Validates and sanitizes input data when creating new categories.

    Attributes:     name: Category name with length validation
    is_active: Optional active status flag (defaults to True if not
    provided)
    """

    name: str = name_field(...)
    is_active: bool | None = None


class ResponseCategorySchema(CreateCategorySchema):
    """Schema for category response data.

    Extends creation schema with system-generated fields for complete
    category representation in API responses.

    Attributes:     id: System-generated category identifier
    is_active: Current active status (always included in response)
    created_at: Timestamp of category creation     updated_at: Timestamp
    of last category modification
    """

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateCategorySchema(BaseModel):
    """Schema for category updates with partial data support.

    Allows partial updates of category properties with all fields
    optional. Used for PATCH operations where only specific fields need
    modification.

    Attributes:     name: Optional category name update     is_active:
    Optional active status update
    """

    name: str | None = name_field(None)
    is_active: bool | None = None
