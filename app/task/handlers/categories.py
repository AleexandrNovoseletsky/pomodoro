"""HTTP-роуты для категорий (categories).

Роуты защищены зависимостями ролей там, где это нужно.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies.auth import require_roles
from app.task.dependencies.category import get_category_service
from app.task.models.categories import Category
from app.task.schemas.category import (
    CreateCategorySchema,
    ResponseCategorySchema,
    UpdateCategorySchema,
)
from app.task.services.category_service import CategoryService
from app.user.models.users import UserRole

category_service_annotated = Annotated[
    CategoryService, Depends(get_category_service)
]
admin = UserRole.ADMIN
root = UserRole.ROOT
require_roles_depends = Depends(
    dependency=require_roles(allowed_roles=(root, admin))
)
router = APIRouter()


@router.get(path="/", response_model=list[ResponseCategorySchema])
async def get_categories(
    category_service: category_service_annotated,
) -> list[ResponseCategorySchema]:
    return await category_service.get_all_objects()


@router.post(
    path="/",
    response_model=ResponseCategorySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_roles_depends],
)
async def create_category(
    body: CreateCategorySchema,
    category_service: category_service_annotated,
) -> Category:
    return await category_service.create_object(object_data=body)


@router.patch(
    path="/{category_id}",
    response_model=ResponseCategorySchema,
    dependencies=[require_roles_depends],
)
async def update_category(
    category_id: int,
    body: UpdateCategorySchema,
    category_service: category_service_annotated,
) -> Category:
    return await category_service.update_object(
        object_id=category_id, update_data=body
    )


@router.delete(
    path="/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_roles_depends],
)
async def delete_category(
    category_id: int,
    category_service: category_service_annotated,
) -> None:
    return await category_service.delete_object(object_id=category_id)
