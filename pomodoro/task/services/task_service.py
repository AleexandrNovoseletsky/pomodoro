"""Task services.

Provides business logic layer for task operations with caching and media
integration. Extends base CRUD service with task-specific functionality
including cache management and media cleanup during operations.
"""

from typing import TypeVar

from pydantic import BaseModel

from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.models.files import OwnerType
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.cache_tasks import TaskCacheRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.task.schemas.task import ResponseTaskSchema, UpdateTaskSchema


class TaskService(CRUDService[ResponseTaskSchema]):
    """Task service inheriting from base CRUD service.

    Extends base CRUD operations with task-specific business logic
    including Redis caching, media file management, and cache
    invalidation.

    Attributes:
        media_service: Media service instance for file operations
        cache_repo: Cache repository for Redis operations
        task_repo: Task repository for data access
        response_schema: Response schema for data serialization
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        cache_repo: TaskCacheRepository,
        media_service: MediaService,
    ):
        """Initialize task service with dependencies.

        Args:     task_repo: Task repository for database operations
        cache_repo: Cache repository for Redis operations
        media_service: Media service for file management
        """
        self.media_service = media_service
        self.cache_repo = cache_repo
        self.task_repo = task_repo
        super().__init__(
            repository=task_repo, response_schema=ResponseTaskSchema
        )

    async def get_all_objects(self) -> list[ResponseTaskSchema]:
        """Retrieve all tasks with cache fallback strategy.

        Implements cache-first approach: attempts to retrieve tasks from
        Redis cache, falls back to database query on cache miss, and
        populates cache for future requests.

        Returns:     List of validated task schemas from cache or
        database

        Note:     Cache population occurs automatically on cache miss to
        ensure     subsequent requests benefit from cached data
        """
        # Attempt to retrieve tasks from cache
        cache_tasks = await self.cache_repo.get_all_tasks()
        if cache_tasks is not None:
            return cache_tasks

        # Fallback to database query on cache miss
        db_tasks = await super().get_all_objects()
        await self.cache_repo.set_all_tasks(tasks=db_tasks)
        return db_tasks

    async def create_object(
        self, object_data: BaseModel
    ) -> ResponseTaskSchema:
        """Create task with author context and cache refresh.

        Args:     object_data: Task creation data including author
        information

        Returns:     Newly created task schema

        Note:     Automatically refreshes cache to maintain data
        consistency
        """
        new_task = await super().create_object(object_data=object_data)
        await self._refresh_cache()
        return new_task

    async def update_object(
        self,
        object_id: int,
        update_data: UpdateTaskSchema,
    ) -> ResponseTaskSchema:
        """Update task and refresh cache for data consistency.

        Args:     object_id: Task identifier to update     update_data:
        Partial task data for update operation

        Returns:     Updated task schema

        Note:     Cache refresh ensures all clients see consistent data
        after updates
        """
        updated_task = await super().update_object(
            object_id=object_id, update_data=update_data
        )
        # Refresh cache after modification
        await self._refresh_cache()
        return updated_task

    async def delete_object(self, object_id: int) -> None:
        """Delete task with media cleanup and cache refresh.

        Performs complete task deletion including: - Removal of
        associated media files - Database record deletion - Cache
        refresh for data consistency

        Args:     object_id: Task identifier to delete

        Note:     Ensures proper cleanup of media files and cache
        invalidation     to prevent orphaned data
        """
        # Clean up associated media files
        await self.media_service.delete_all_by_owner(
            domain=OwnerType.TASK, owner_id=object_id
        )
        # Delete task from database
        await super().delete_object(object_id=object_id)
        # Refresh cache after deletion
        await self._refresh_cache()

    async def _refresh_cache(self):
        """Private method for cache refresh and synchronization.

        Updates Redis cache with current database state to ensure cache
        consistency after create, update, or delete operations.
        """
        db_tasks = await self.task_repo.get_all_objects()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await self.cache_repo.set_all_tasks(task_schema)
