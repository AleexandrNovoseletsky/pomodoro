"""Сервисы задач."""

from typing import TypeVar

from pydantic import BaseModel

from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.cache_tasks import TaskCacheRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.task.schemas.task import ResponseTaskSchema
from pomodoro.user.schemas.user import ResponseUserProfileSchema

# Подсказка типов для базового класса CRUDService
# О том, что схемы создания и изминения модели унаследованы от базового класса
TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)


class TaskService(CRUDService):
    """Сервис задач. Унаследован от базового сервиса."""

    def __init__(
        self,
        task_repo: TaskRepository,
        cache_repo: TaskCacheRepository,
        media_service: MediaService,
    ):
        """Инициализирует сервис задач."""
        self.media_service = media_service
        super().__init__(
            repository=task_repo, response_schema=ResponseTaskSchema
        )
        self.cache_repo = cache_repo
        self.task_repo = task_repo

    async def get_all_objects(self) -> list[ResponseTaskSchema]:
        """Получение всех задач и кэширование при необходимости."""
        # Пытаемся получить задачи из кэша
        cache_tasks = await self.cache_repo.get_all_tasks()
        if cache_tasks is not None:
            return cache_tasks

        # Если нет — получаем из БД через базовый CRUD
        db_tasks = await super().get_all_objects()
        await self.cache_repo.set_all_tasks(tasks=db_tasks)
        return db_tasks

    async def create_with_author(
        self,
        object_data: TCreate,
        current_user: ResponseUserProfileSchema,
    ) -> ResponseTaskSchema:
        """Создаёт задачу с автором (current_user)."""
        new_task = await super().create_object_with_author(
            object_data=object_data, current_user=current_user
        )
        await self._refresh_cache()
        return new_task

    async def update_object(
        self,
        object_id: int,
        update_data: TUpdate,
    ) -> ResponseTaskSchema:
        """Изминение задачи и обновление кэша."""
        updated_task = await super().update_object(
            object_id=object_id, update_data=update_data
        )
        # после изминения обновляем кэш
        await self._refresh_cache()
        return updated_task

    async def delete_object(self, object_id: int) -> None:
        """Удаление задачи и обновление кэша."""
        # Очищаем файлы
        await self.media_service.delete_all_by_owner(
            owner_type="task", owner_id=object_id
            )
        # Удаляем задачу из БД
        await super().delete_object(object_id=object_id)
        # после удаления обновляем кэш
        await self._refresh_cache()

    async def _refresh_cache(self):
        """Приватный метод для обновления кэша."""
        db_tasks = await self.task_repo.get_all_objects()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await self.cache_repo.set_all_tasks(task_schema)
