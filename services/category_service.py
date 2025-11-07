from repositories import CategoryRepository
from services.base_crud import CRUDService


class CategoryService(CRUDService):
    def __init__(
        self,
        repository: CategoryRepository,
    ):
        super().__init__(repository=repository)
