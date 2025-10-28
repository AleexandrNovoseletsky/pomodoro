from fastapi import APIRouter, Depends, status

from auth.permissions import require_roles
from dependencies import get_category_service
from models import Categories
from schemas import (
    CreateCategorySchema, ResponseCategorySchema, UpdateCategorySchema
)
from services import CategoryService

router = APIRouter(prefix='/categories', tags=['categories'])


@router.get(path='/', response_model=list[ResponseCategorySchema])
async def get_categories(
        category_service: CategoryService = Depends(
            get_category_service
        )
) -> list[ResponseCategorySchema]:
    return await category_service.get_all_objects()


@router.post(
    path='/',
    response_model=ResponseCategorySchema,
    dependencies=[Depends(require_roles('root', 'admin'))]
)
async def create_category(
        new_category: CreateCategorySchema,
        category_service = Depends(get_category_service)
) -> Categories:
    return await category_service.create_object(new_category)


@router.patch(
    path='/',
    response_model=ResponseCategorySchema,
    dependencies=[Depends(require_roles('root', 'admin'))]
)
async def update_category(
        category_id: int,
        update_data: UpdateCategorySchema,
        category_service = Depends(get_category_service)
) -> Categories:
    return await category_service.update_object(
        category_id, update_data
    )


@router.delete(
    path='/{category_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles('root', 'admin'))]
)
async def delete_category(
        category_id: int,
        category_service = Depends(get_category_service)
) -> None:
    return await category_service.delete_object(category_id)
