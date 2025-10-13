from fastapi import APIRouter, Depends, status

from database.models import Categories
from dependecy import get_category_repository
from schemas.Category import CreateCategory, ResponseCategory

router = APIRouter(prefix='/categories', tags=['categories'])

@router.get('/', response_model=list[ResponseCategory])
async def get_categories(repo = Depends(get_category_repository)):
    return repo.get_categories()

@router.post('/', response_model=ResponseCategory)
async def create_category(
        category: CreateCategory,
        repo = Depends(get_category_repository)
):
    category_orm = Categories(name=category.name)
    return repo.create_category(category_orm)

@router.delete('/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int,
        repo = Depends(get_category_repository)
) -> None:
    return repo.delete_category(category_id)
