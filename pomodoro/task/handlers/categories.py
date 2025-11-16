"""HTTP-роуты для категорий (categories).

Роуты защищены зависимостями ролей там, где это нужно.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from pomodoro.auth.dependencies.auth import require_roles
from pomodoro.task.dependencies.category import get_category_service
from pomodoro.task.models.categories import Category
from pomodoro.task.schemas.category import (
    CreateCategorySchema,
    ResponseCategorySchema,
    UpdateCategorySchema,
)
from pomodoro.task.services.category_service import CategoryService

category_service_annotated = Annotated[
    CategoryService, Depends(get_category_service)
]
only_admin = Depends(
    dependency=require_roles(allowed_roles=("root", "admin"))
)
router = APIRouter()


@router.get(path="/", response_model=list[ResponseCategorySchema])
async def get_categories(
    category_service: category_service_annotated,
) -> list[ResponseCategorySchema]:
    """Получить все категории. Доступно всем."""
    return await category_service.get_all_objects()


@router.post(
    path="/",
    response_model=ResponseCategorySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[only_admin],
)
async def create_category(
    body: CreateCategorySchema,
    category_service: category_service_annotated,
) -> Category:
    """Создать категорию. Доступно алминистраторам."""
    return await category_service.create_object(object_data=body)


@router.patch(
    path="/{category_id}",
    response_model=ResponseCategorySchema,
    dependencies=[only_admin],
)
async def update_category(
    category_id: int,
    body: UpdateCategorySchema,
    category_service: category_service_annotated,
) -> Category:
    """Изменить категорию. Доступно администраторам."""
    return await category_service.update_object(
        object_id=category_id, update_data=body
    )


@router.delete(
    path="/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[only_admin],
)
async def delete_category(
    category_id: int,
    category_service: category_service_annotated,
) -> None:
    """Удалить категорию. Доступно администраторам."""
    return await category_service.delete_object(object_id=category_id)
