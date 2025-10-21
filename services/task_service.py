from typing import List
from repository.task import TaskRepository
from repository.cache_tasks import TaskCacheRepository
from schemas.Task import ResponseTaskSchema, CreateTaskSchema, UpdateTaskSchema
from database.models import Tasks


class TaskService:
    def __init__(
            self,
            task_repo: TaskRepository,
            cache_repo: TaskCacheRepository
    ):
        self.task_repo = task_repo
        self.cache_repo = cache_repo

    async def get_all_tasks(self) -> List[ResponseTaskSchema]:
        # Пытаемся получить из кэша
        cache_tasks = await self.cache_repo.get_all_tasks()
        if cache_tasks is not None:
            return cache_tasks

        # Если нет в кэше - получаем из БД и сохраняем в кэш
        db_tasks = self.task_repo.get_tasks()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await self.cache_repo.set_all_tasks(task_schema)
        return task_schema

    async def create_task(self, task_data: CreateTaskSchema) -> Tasks:
        new_task = self.task_repo.create_task(task_data)
        # Обновляем кэш при создании новой задачи
        db_tasks = self.task_repo.get_tasks()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await self.cache_repo.set_all_tasks(task_schema)
        return new_task

    async def update_task(
            self,
            task_id: int,
            update_data: UpdateTaskSchema
    ) -> Tasks:
        updated_task = self.task_repo.update_task_name(
            task_id,
            update_data
        )
        # Обновляем кэш при обновлении
        db_tasks = self.task_repo.get_tasks()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await self.cache_repo.set_all_tasks(task_schema)
        return updated_task

    async def delete_task(self, task_id: int) -> None:
        self.task_repo.delete_task(task_id)
        # Обновляем кэш при удалении
        db_tasks = self.task_repo.get_tasks()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await self.cache_repo.set_all_tasks(task_schema)
