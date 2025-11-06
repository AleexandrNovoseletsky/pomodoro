from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependencies import get_category_service, require_roles
from models import Categories
from schemas import CreateCategorySchema, ResponseCategorySchema, UpdateCategorySchema
from services import CategoryService

category_service_annotated = Annotated[CategoryService, Depends(get_category_service)]
require_roles_depends = Depends(
    dependency=require_roles(allowed_roles=("root", "admin"))
)
router = APIRouter(prefix="/categories", tags=["categories"])


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
) -> Categories:
    return await category_service.create_object(object_data=body)


@router.patch(
    path="/",
    response_model=ResponseCategorySchema,
    dependencies=[require_roles_depends],
)
async def update_category(
    category_id: int,
    body: UpdateCategorySchema,
    category_service: category_service_annotated,
) -> Categories:
    return await category_service.update_object(object_id=category_id, update_data=body)


@router.delete(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_roles_depends],
)
async def delete_category(
    category_id: int,
    category_service: category_service_annotated,
) -> None:
    return await category_service.delete_object(object_id=category_id)
