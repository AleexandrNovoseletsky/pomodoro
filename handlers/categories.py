from fastapi import APIRouter, Depends, status

from dependecy import get_category_service
from schemas import CreateCategorySchema, ResponseCategorySchema, UpdateCategorySchema

router = APIRouter(prefix='/categories', tags=['categories'])

@router.get('/', response_model=list[ResponseCategorySchema])
async def get_categories(category_service = Depends(get_category_service)):
    return await category_service.get_all_categories()

@router.post('/', response_model=ResponseCategorySchema)
async def create_category(
        new_category: CreateCategorySchema,
        category_service = Depends(get_category_service)
):
    return await category_service.create_category(new_category)

@router.patch('/', response_model=ResponseCategorySchema)
async def update_category(
        category_id: int,
        update_data: UpdateCategorySchema,
        category_service = Depends(get_category_service)
):
    return await category_service.update_category(category_id, update_data)

@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int,
        category_service = Depends(get_category_service)
) -> None:
    return await category_service.delete_category(category_id)
