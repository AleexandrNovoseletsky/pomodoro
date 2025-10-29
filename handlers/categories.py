from fastapi import APIRouter, Depends, status
from typing import Annotated

from dependencies import get_category_service, require_roles
from models import Categories
from schemas import CreateCategorySchema, ResponseCategorySchema, UpdateCategorySchema
from services import CategoryService

allowed_roles = require_roles(allowed_roles=("root", "admin"))
router = APIRouter(prefix="/categories", tags=["categories"])


@router.get(path="/", response_model=list[ResponseCategorySchema])
async def get_categories(
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> list[ResponseCategorySchema]:
    return await category_service.get_all_objects()


@router.post(
    path="/",
    response_model=ResponseCategorySchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allowed_roles)],
)
async def create_category(
    body: CreateCategorySchema,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> Categories:
    return await category_service.create_object(body)


@router.patch(
    path="/",
    response_model=ResponseCategorySchema,
    dependencies=[Depends(allowed_roles)],
)
async def update_category(
    category_id: int,
    body: UpdateCategorySchema,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> Categories:
    return await category_service.update_object(category_id, body)


@router.delete(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(allowed_roles)],
)
async def delete_category(
    category_id: int,
    category_service: Annotated[CategoryService, Depends(get_category_service)],
) -> None:
    return await category_service.delete_object(category_id)
