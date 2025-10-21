# services/task_service.py
from typing import List
from repository.task import TaskRepository
from repository.cache_tasks import TaskCacheRepository
from schemas.Task import ResponseTaskSchema, CreateTaskSchema
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
        if cache_tasks:
            return cache_tasks

        # Если нет в кэше - получаем из БД и сохраняем в кэш
        db_tasks = self.task_repo.get_tasks()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await self.cache_repo.set_all_tasks(task_schema)
        return task_schema

    async def create_task(self, task_data: CreateTaskSchema) -> Tasks:
        task = self.task_repo.create_task(task_data)
        # Инвалидируем кэш при создании новой задачи
        await self.cache_repo.set_all_tasks(None)
        return task

    async def update_task_name(self, task_id: int, name: str) -> Tasks:
        task = self.task_repo.update_task_name(task_id, name)
        # Инвалидируем кэш при обновлении
        await self.cache_repo.set_all_tasks(None)
        return task

    async def delete_task(self, task_id: int) -> None:
        self.task_repo.delete_task(task_id)
        # Инвалидируем кэш при удалении
        await self.cache_repo.set_all_tasks(None)