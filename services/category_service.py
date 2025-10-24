from typing import List

from fastapi import HTTPException

from models.categories import Categories
from repositories import CategoryRepository
from schemas import ResponseCategorySchema, CreateCategorySchema, UpdateCategorySchema


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def get_all_categories(self) -> List[ResponseCategorySchema]:
        db_categories = await self.category_repo.get_categories()
        category_schema = [
            ResponseCategorySchema.model_validate(category)
            for category in db_categories
        ]
        return category_schema

    async def create_category(
            self,
            category_data: CreateCategorySchema
    ) -> Categories:
        new_category = await self.category_repo.create_category(category_data)
        return new_category

    async def update_category(
            self,
            category_id: int,
            update_data: UpdateCategorySchema
    ) -> Categories:
        updated_category = await self.category_repo.update_category(
            category_id, update_data
        )
        if updated_category is None:
            raise HTTPException(
                status_code=404,
                detail=f'категория с id={category_id} не найдена.'
            )
        return updated_category

    async def delete_category(self, category_id: int) -> None:
        deleted = await self.category_repo.delete_category(category_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f'категория с id={category_id} не найдена.'
            )
        return None
