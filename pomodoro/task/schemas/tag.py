"""Tag schemas.

Defines Pydantic schemas for tag data validation, serialization, and
API communication. Includes schemas for creation, database operations,
response, and update operations with proper field constraints and
validation rules.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from pomodoro.core.settings import Settings

settings = Settings()


class CreateTagSchema(BaseModel):
    """Schema for tag creation.

    Validates and sanitizes input data when creating new tag via API.

    Attributes:
        name: Tag name with length validation
        is_active: Optional active status flag
    """

    name: str = Field(..., max_length=settings.MAX_TAG_NAME_LENGTH)
    is_active: bool | None = None


class CreateTagORM(CreateTagSchema):
    """Schema for tag creation in database operations.

    Extends creation schema with system-generated author identifier for
    internal database operations.

    Attributes:
        author_id: System-provided identifier of tag
                    creator
    """

    author_id: int


class ResponseTagSchema(CreateTagSchema):
    """Schema for tag response data.

    Extends creation schema with system-generated fields for complete
    tag representation in API responses.

    Attributes:
         id: System-generated tag identifier
         author_id: Identifier of tag creator
         is_active: Current active status
        created_at: Timestamp of tag creation
        updated_at: Timestamp of last tag modification
    """

    id: int
    author_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateTagSchema(BaseModel):
    """Schema for tag updates with partial data support.

    Allows partial updates of tag properties with all fields optional.
    Used for PATCH operations where only specific fields need
    modification.

    Attributes:
        name: Optional tag name update
        is_active: Optional active status update
    """

    name: str | None = Field(None, max_length=settings.MAX_TAG_NAME_LENGTH)
    is_active: bool | None = None
