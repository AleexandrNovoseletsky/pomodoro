from app.task.repositories.category import CategoryRepository
from app.core.services.base_crud import CRUDService
from app.task.schemas.category import ResponseCategorySchema


class CategoryService(CRUDService):
    def __init__(
        self,
        category_repo: CategoryRepository,
    ):
        super().__init__(
            repository=category_repo, response_schema=ResponseCategorySchema
        )
