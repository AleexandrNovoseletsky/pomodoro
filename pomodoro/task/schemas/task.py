"""Task schemas.

Defines Pydantic schemas for task data validation, serialization, and
API communication. Includes schemas for creation, database operations,
response, and update operations with proper field constraints and
validation rules.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from pomodoro.core.settings import Settings

settings = Settings()


def name_field(default: Any):
    """Field constraints for task name length validation.

    Args:     default: Default value for the field

    Returns:     Field configuration with length constraints and
    description
    """
    return Field(
        default,
        min_length=settings.MIN_TASK_NAME_LENGTH,
        max_length=settings.MAX_TASK_NAME_LENGTH,
        description="Task name",
    )


def pomodoro_count_field(default: Any):
    """Field constraints for pomodoro count duration validation.

    Args:     default: Default value for the field

    Returns:     Field configuration with minimum and maximum value
    constraints
    """
    return Field(
        default, ge=settings.MIN_POMODORO_COUNT, le=settings.MAX_POMODORO_COUNT
    )


class CreateTaskSchema(BaseModel):
    """Schema for task creation with user-provided data.

    Validates and sanitizes input data when creating new tasks via API.

    Attributes:     name: Task name with length validation
    pomodoro_count: Number of pomodoro intervals with range validation
    category_id: Associated category identifier     is_active: Optional
    active status flag
    """

    name: str = name_field(...)
    pomodoro_count: int = pomodoro_count_field(...)
    category_id: int
    is_active: bool | None = None


class CreateTaskORM(CreateTaskSchema):
    """Schema for task creation in database operations.

    Extends creation schema with system-generated author identifier for
    internal database operations.

    Attributes:     author_id: System-provided identifier of task
    creator
    """

    author_id: int


class ResponseTaskSchema(CreateTaskSchema):
    """Schema for task response data.

    Extends creation schema with system-generated fields for complete
    task representation in API responses.

    Attributes:     id: System-generated task identifier     author_id:
    Identifier of task creator     is_active: Current active status
    created_at: Timestamp of task creation     updated_at: Timestamp of
    last task modification
    """

    id: int
    author_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateTaskSchema(BaseModel):
    """Schema for task updates with partial data support.

    Allows partial updates of task properties with all fields optional.
    Used for PATCH operations where only specific fields need
    modification.

    Attributes:     name: Optional task name update     pomodoro_count:
    Optional pomodoro count update     category_id: Optional category
    reassignment     is_active: Optional active status update
    """

    name: str | None = name_field(None)
    pomodoro_count: int | None = pomodoro_count_field(None)
    category_id: int | None = None
    is_active: bool | None = None
