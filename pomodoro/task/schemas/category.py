"""Category schemas.

Defines Pydantic schemas for category validation, serialization, and
API responses. Supports hierarchical (tree-based) category structures
with parent-child relationships.

This module intentionally separates:
- CRUD schemas (flat structure)
- Read-only tree schemas (hierarchical structure)

Tree relationships (children) are computed in the service layer and
are NOT persisted in the database.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from pomodoro.core.settings import Settings

settings = Settings()


# ---------------------------------------------------------------------
# Base schemas
# ---------------------------------------------------------------------


class CategoryBaseSchema(BaseModel):
    """Base schema for category data.

    Contains fields shared across all category schemas.
    """

    id: int
    name: str = Field(
        ...,
        min_length=settings.MIN_CATEGORY_NAME_LENGTH,
        max_length=settings.MAX_CATEGORY_NAME_LENGTH,
        description="Category name",
    )
    is_active: bool

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------
# Create / Update schemas
# ---------------------------------------------------------------------


class CreateCategorySchema(BaseModel):
    """Schema for category creation.

    Used when creating a new category. Supports optional parent
    assignment to build category hierarchy.
    """

    name: str = Field(
        ...,
        min_length=settings.MIN_CATEGORY_NAME_LENGTH,
        max_length=settings.MAX_CATEGORY_NAME_LENGTH,
        description="Category name",
    )
    parent_id: int | None = Field(
        default=None,
        description="Parent category ID (for nested categories)",
    )
    is_active: bool | None = Field(
        default=True,
        description="Category active status",
    )


class UpdateCategorySchema(BaseModel):
    """Schema for partial category updates.

    All fields are optional to support PATCH semantics.
    """

    name: str | None = Field(
        default=None,
        min_length=settings.MIN_CATEGORY_NAME_LENGTH,
        max_length=settings.MAX_CATEGORY_NAME_LENGTH,
        description="Updated category name",
    )
    parent_id: int | None = Field(
        default=None,
        description="Updated parent category ID",
    )
    is_active: bool | None = Field(
        default=None,
        description="Updated active status",
    )


# ---------------------------------------------------------------------
# Flat response schema (single category)
# ---------------------------------------------------------------------


class ResponseCategorySchema(CategoryBaseSchema):
    """Schema for single category response.

    Used for:
    - get-by-id
    - create
    - update responses

    Does NOT include children.
    """

    parent_id: int | None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------
# Tree response schema
# ---------------------------------------------------------------------


class CategoryTreeSchema(CategoryBaseSchema):
    """Schema for hierarchical category tree.

    Represents a category node with all nested children.
    This schema is read-only and built dynamically in the service layer.
    """

    children: list[CategoryTreeSchema] = Field(
        default_factory=list,
        description="Nested child categories",
    )
