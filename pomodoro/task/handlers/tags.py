"""HTTP routes for tags.

Provides REST API endpoints for tag management operations.
Routes are protected with role-based dependencies where necessary.
Includes CRUD operations with appropriate authorization checks.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from pomodoro.auth.dependencies.auth import require_roles
from pomodoro.task.dependencies.tag import get_tag_service
from pomodoro.task.schemas.tag import (
    CreateTagORM,
    CreateTagSchema,
    ResponseTagSchema,
    UpdateTagSchema,
)
from pomodoro.task.services.tag_service import TagService
from pomodoro.user.dependencies.user import get_current_user
from pomodoro.user.models.users import UserProfile, UserRole

# Dependency annotations for consistent type checking and IDE support
tag_service_annotated = Annotated[
    TagService, Depends(get_tag_service)
]

# Admin-only dependency for privileged operations
only_admin = Depends(
    dependency=require_roles(
        allowed_roles=(UserRole.ROOT, UserRole.ADMIN)
    )
)

current_user_annotated = Annotated[
    UserProfile, Depends(get_current_user)
]

router = APIRouter()


@router.get(
    path="/",
    response_model=list[ResponseTagSchema],
    summary="Get all tags",
    description="Get list of all available tags. Public access."
)
async def get_tags(
    tag_service: tag_service_annotated,
) -> list[ResponseTagSchema]:
    """Get all tags. Available to all users."""
    return await tag_service.get_all_objects()


@router.post(
    path="/",
    response_model=ResponseTagSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[only_admin],
    summary="Create tag",
    description="Create new tag. Administrator privileges required."
)
async def create_tag(
    body: CreateTagSchema,
    tag_service: tag_service_annotated,
    current_user: current_user_annotated,
) -> ResponseTagSchema:
    """Create category. Available to administrators only."""
    create_tag_orm = CreateTagORM(
        **body.model_dump(), author_id=current_user.id
    )
    return await tag_service.create_object(object_data=create_tag_orm)


@router.patch(
    path="/{tag_id}",
    response_model=ResponseTagSchema,
    dependencies=[only_admin],
    summary="Update tag",
    description=("Update an existing tag. "
                 "Administrator rights required.")
)
async def update_category(
    tag_id: int,
    body: UpdateTagSchema,
    tag_service: tag_service_annotated,
) -> ResponseTagSchema:
    """Update tag. Available to administrators only."""
    return await tag_service.update_object(
        object_id=tag_id, update_data=body
    )


@router.delete(
    path="/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[only_admin],
    summary="Delete tag",
    description="Permanently deletes a tag. Administrator rights required"
)
async def delete_tag(
    tag_id: int,
    tag_service: tag_service_annotated,
) -> None:
    """Delete tag. Available to administrators only."""
    return await tag_service.delete_object(object_id=tag_id)
