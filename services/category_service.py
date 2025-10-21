from typing import List

from database.models import Categories
from repository.category import CategoryRepository
from schemas.Category import ResponseCategorySchema, CreateCategorySchema, UpdateCategorySchema


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def get_all_categories(self) -> List[ResponseCategorySchema]:
        db_categories = self.category_repo.get_categories()
        category_schema = [
            ResponseCategorySchema.model_validate(category)
            for category in db_categories
        ]
        return category_schema

    def create_category(
            self,
            category_data: CreateCategorySchema
    ) -> Categories:
        new_category = self.category_repo.create_category(category_data)
        return new_category

    def update_category(
            self,
            category_id: int,
            update_data: UpdateCategorySchema
    ) -> Categories:
        updated_category = self.category_repo.update_category(
            category_id, update_data
        )
        return updated_category

    def delete_category(self, category_id: int) -> None:
        return self.category_repo.delete_category(category_id)
