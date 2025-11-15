"""Сервисы категорий."""

from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.schemas.category import ResponseCategorySchema


class CategoryService(CRUDService):
    """Сервис категорий. Унаследован от базового сервиса."""

    def __init__(
        self,
        category_repo: CategoryRepository,
        media_service: MediaService,
    ):
        """Инициализирует сервис категорий."""
        self.media_service = media_service
        super().__init__(
            repository=category_repo, response_schema=ResponseCategorySchema
        )

    async def delete_object(self, object_id):
        """Удаление категории."""
        # Очищаем файлы
        await self.media_service.delete_all_by_owner(
            owner_type="category", owner_id=object_id
            )
        return await super().delete_object(object_id)
