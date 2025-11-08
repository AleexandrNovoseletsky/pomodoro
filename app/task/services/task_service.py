from typing import List, TypeVar

from pydantic import BaseModel

from app.task.repositories.cache_tasks import TaskCacheRepository
from app.task.repositories.task import TaskRepository
from app.task.schemas.task import ResponseTaskSchema
from app.user.schemas.user import ResponseUserProfileSchema
from app.core.services.base_crud import CRUDService


TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)


class TaskService(CRUDService):
    def __init__(
        self, task_repo: TaskRepository, cache_repo: TaskCacheRepository
    ):
        super().__init__(
            repository=task_repo, response_schema=ResponseTaskSchema
        )
        self.cache_repo = cache_repo
        self.task_repo = task_repo

    async def get_all_objects(self) -> List[ResponseTaskSchema]:
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
    ):
        """Создать задачу и записать автора (current_user).

        Исправлено: не вызывать рекурсивно метод самого себя — используем
        базовый метод `create_object_with_author` из CRUDService.
        """
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
        updated_task = await super().update_object(
            object_id=object_id, update_data=update_data
        )
        # после обновления обновляем кэш
        await self._refresh_cache()
        return updated_task

    async def delete_object(self, object_id: int) -> None:
        await super().delete_object(object_id=object_id)
        # после удаления обновляем кэш
        await self._refresh_cache()

    async def _refresh_cache(self):
        """Приватный метод для обновления Redis-кэша."""
        db_tasks = await self.task_repo.get_all_objects()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await self.cache_repo.set_all_tasks(task_schema)
