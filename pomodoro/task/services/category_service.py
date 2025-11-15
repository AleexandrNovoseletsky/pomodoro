"""Сервисы категорий."""

from pomodoro.core.services.base_crud import CRUDService
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.schemas.category import ResponseCategorySchema


class CategoryService(CRUDService):
    """Сервис категорий. Унаследован от базового сервиса."""

    def __init__(
        self,
        category_repo: CategoryRepository,
    ):
        """Инициализирует сервис категорий."""
        super().__init__(
            repository=category_repo, response_schema=ResponseCategorySchema
        )
