"""HTTP routes for categories.

Provides REST API endpoints for category management operations.
Routes are protected with role-based dependencies where necessary.
Includes CRUD operations with appropriate authorization checks.
"""

from typing import Annotated, Any, Coroutine

from fastapi import APIRouter, Depends, status

from pomodoro.auth.dependencies.auth import require_roles
from pomodoro.task.dependencies.category import get_category_service
from pomodoro.task.schemas.category import (
    CreateCategorySchema,
    ResponseCategorySchema,
    UpdateCategorySchema, CategoryTreeSchema,
)
from pomodoro.task.services.category_service import CategoryService
from pomodoro.user.models.users import UserRole

# Dependency annotations for consistent type checking and IDE support
category_service_annotated = Annotated[
    CategoryService, Depends(get_category_service)
]

# Admin-only dependency for privileged operations
only_admin = Depends(
    dependency=require_roles(
        allowed_roles=(UserRole.ROOT, UserRole.ADMIN)
    )
)

router = APIRouter()


@router.get(
    path="/",
    response_model=list[ResponseCategorySchema],
    summary="Получить все категории",
    description="Получить список всех доступных категорий. Открытый доступ."
)
async def get_categories(
    category_service: category_service_annotated,
) -> list[ResponseCategorySchema]:
    """Get all categories. Available to all users."""
    return await category_service.get_all_objects()


@router.get(
    path="/tree",
    response_model=list[CategoryTreeSchema],
    summary="Получить дерево категорий",
    description=(
        "Возвращает иерархическое дерево всех категорий "
        "с вложенными подкатегориями."
    ),
)
async def get_category_tree(
    category_service: category_service_annotated,
) -> list[ResponseCategorySchema]:
    """Get full category tree.

    Returns categories structured as a tree with nested children.
    Available to all users.
    """
    return await category_service.get_tree()


@router.get(
    path="/{category_id}/tree",
    response_model=CategoryTreeSchema,
    summary="Получить поддерево категории",
    description=(
        "Возвращает указанную категорию и все её вложенные подкатегории "
        "в виде дерева."
    ),
)
async def get_category_subtree(
    category_id: int,
    category_service: category_service_annotated,
) -> ResponseCategorySchema:
    """Get category subtree.

    Returns the specified category with all nested child categories.
    Available to all users.
    """
    return await category_service.get_subtree(category_id=category_id)


@router.post(
    path="/",
    response_model=ResponseCategorySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[only_admin],
    summary="Создать категорию",
    description="Создание новой категории. Требуются права администратора."
)
async def create_category(
    body: CreateCategorySchema,
    category_service: category_service_annotated,
) -> ResponseCategorySchema:
    """Create category. Available to administrators only."""
    return await category_service.create_object(object_data=body)


@router.patch(
    path="/{category_id}",
    response_model=ResponseCategorySchema,
    dependencies=[only_admin],
    summary="Обновить категорию",
    description=("Обновление существующей категории. "
                 "Требуются права администратора.")
)
async def update_category(
    category_id: int,
    body: UpdateCategorySchema,
    category_service: category_service_annotated,
) -> ResponseCategorySchema:
    """Update category. Available to administrators only."""
    return await category_service.update_object(
        object_id=category_id, update_data=body
    )


@router.delete(
    path="/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[only_admin],
    summary="Удалить категорию",
    description="Необратимо удаляет категорию. Требуются права администратора"
)
async def delete_category(
    category_id: int,
    category_service: category_service_annotated,
) -> None:
    """Delete category. Available to administrators only."""
    return await category_service.delete_object(object_id=category_id)
