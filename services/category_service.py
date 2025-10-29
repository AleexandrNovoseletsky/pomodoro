from repositories import CategoryRepository
from schemas import ResponseCategorySchema
from services.crud import CRUDService


class CategoryService(CRUDService):
    def __init__(
        self,
        repository: CategoryRepository,
    ):
        super().__init__(repository=repository, response_schema=ResponseCategorySchema)
