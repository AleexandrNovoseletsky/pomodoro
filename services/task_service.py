from typing import List

from auth import require_owner, require_role
from custom_exceptions import AccessDenied
from models import Tasks
from repositories import TaskCacheRepository
from repositories import TaskRepository
from schemas import ResponseTaskSchema, CreateTaskSchema, UpdateTaskSchema
from schemas.task import CreateTaskORM
from services.crud import CRUDService


class TaskService(CRUDService):
    def __init__(self, task_repo: TaskRepository, cache_repo: TaskCacheRepository):
        super().__init__(repository=task_repo, response_schema=ResponseTaskSchema)
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

    async def create_object(
        self,
        object_data: CreateTaskSchema,
        current_user: dict | None = None,
    ) -> Tasks:
        user_id = current_user["user_id"]
        task_data = object_data.model_dump()
        task_data["author_id"] = user_id
        create_object_data = CreateTaskORM(**task_data)
        new_task = await super().create_object(object_data=create_object_data)
        # после создания обновляем кэш
        await self._refresh_cache()
        return new_task

    async def update_object(
        self,
        object_id: int,
        update_data: UpdateTaskSchema,
        current_user: dict | None = None,
    ) -> Tasks:
        updatable_task = await super().get_one_object(object_id=object_id)

        # Если пользователь не передан, выбрасываем исключение.
        if current_user is None:
            raise AccessDenied()

        # Проверяем является ли current_user владельцем обновляемой задачи
        access_owner = await require_owner(
            resource=updatable_task, current_user=current_user
        )

        # Проверяем разрешение на редактирование по роли пользователя.
        access_admin = await require_role(
            current_user=current_user, allowed_roles=("root", "admin")
        )

        if access_owner or access_admin:
            updated_task = await super().update_object(
                object_id=object_id, update_data=update_data
            )
            await self._refresh_cache()
            return updated_task
        raise AccessDenied()

    async def delete_object(self, object_id: int, current_user: dict = None) -> None:
        deletable_task = await super().get_one_object(object_id=object_id)

        # Если пользователь не передан, выбрасываем исключение.
        if current_user is None:
            raise AccessDenied()

        # Проверяем является ли current_user владельцем удаляемой задачи
        access_owner = await require_owner(
            resource=deletable_task, current_user=current_user
        )

        # Проверяем разрешение на редактирование по роли пользователя.
        access_admin = await require_role(
            current_user=current_user, allowed_roles=("root", "admin")
        )

        if access_owner or access_admin:
            await super().delete_object(object_id=object_id)
            await self._refresh_cache()
        else:
            raise AccessDenied()

    async def _refresh_cache(self):
        """Приватный метод для обновления Redis-кэша."""
        db_tasks = await self.task_repo.get_all_objects()
        task_schema = [ResponseTaskSchema.model_validate(task) for task in db_tasks]
        await self.cache_repo.set_all_tasks(task_schema)
