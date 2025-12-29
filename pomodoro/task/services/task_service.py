"""Task services.

Provides business logic layer for task operations with caching and media
integration. Extends base CRUD service with task-specific functionality
including cache management and media cleanup during operations.
"""

from pydantic import BaseModel
from sqlalchemy import select

# Import dependencies
from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.models.files import OwnerType
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.cache_tasks import TaskCacheRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.task.schemas.task import ResponseTaskSchema, UpdateTaskSchema
from pomodoro.task.services.tag_service import TagService


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
        tag_service: TagService,
    ):
        """Initialize task service with dependencies.

        Args:
            task_repo: Task repository for database operations
            cache_repo: Cache repository for Redis operations
            media_service: Media service for file management
            tag_service: Tag service for tag operations
        """
        # Initialize dependencies
        self.media_service = media_service
        self.cache_repo = cache_repo
        self.task_repo = task_repo
        self.tag_service = tag_service
        super().__init__(
            repository=task_repo, response_schema=ResponseTaskSchema
        )

    # Tag validation methods
    async def _validate_tags_exist(self, tag_ids: list[int]) -> None:
        """Validate that all provided tag IDs exist.

        Args:
            tag_ids: List of tag IDs to validate

        Raises:
            ObjectNotFoundError: If any tag does not exist
        """
        for tag_id in tag_ids:
            await self.tag_service.get_one_object(object_id=tag_id)

    async def _update_task_tags(
        self, task_id: int, tag_ids: list[int]
    ) -> None:
        """Update tags associated with a task.

        Args:
            task_id: Task ID to update.
            tag_ids: List of tag IDs to associate with the task.
        """
        async with self.task_repo.sessionmaker() as session:
            async with session.begin():
                # Get the task
                result = await session.execute(
                    select(self.task_repo.orm_model).where(
                        self.task_repo.orm_model.id == task_id
                    )
                )
                task = result.scalars().one_or_none()
                if not task:
                    from pomodoro.core.exceptions.object_not_found import (
                        ObjectNotFoundError,
                    )
                    raise ObjectNotFoundError(task_id)

                # Get tag objects
                from pomodoro.task.models.tags import Tag
                result = await session.execute(
                    select(Tag).where(Tag.id.in_(tag_ids))
                )
                tags = result.scalars().all()

                # Update the relationship
                task.tags = tags

    # Public API methods
    async def get_all_objects(self) -> list[ResponseTaskSchema]:
        """Retrieve all tasks with cache fallback strategy.

        Implements cache-first approach: attempts to retrieve tasks from
        Redis cache, falls back to database query on cache miss, and
        populates cache for future requests.

        Returns:
            List of validated task schemas from cache or
            database

        Note:
            Cache population occurs automatically on cache miss to
            ensure subsequent requests benefit from cached data
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
        """Create task with author context, tag validation and cache refresh.

        Args:
            object_data: Task creation data including author
                         information and tags

        Returns:
            Newly created task schema

        Note:
            Automatically validates tag existence and refreshes cache
            to maintain data consistency
        """
        # Extract tag_ids and validate if provided
        tag_ids = getattr(object_data, 'tags', None)
        if tag_ids:
            await self._validate_tags_exist(tag_ids)

        # Create task without tags (exclude tags from model creation)
        task_data_dict = object_data.model_dump(exclude_unset=True)
        task_data_dict.pop('tags', None)  # Remove tags as it's a relationship
        task_data = type(object_data)(**task_data_dict)

        new_task = await super().create_object(object_data=task_data)

        # Assign tags if provided
        if tag_ids:
            await self._update_task_tags(new_task.id, tag_ids)
            # Refresh to get updated tags
            new_task = await self.task_repo.get_object(object_id=new_task.id)

        await self._refresh_cache()
        return new_task

    async def update_object(
        self,
        object_id: int,
        update_data: UpdateTaskSchema,
    ) -> ResponseTaskSchema:
        """Update task with tag validation and cache refresh.

        Args:
            object_id: Task identifier to update
            update_data: Partial task data for update operation

        Returns:
            Updated task schema

        Note:
            Validates tag existence if tag_ids provided and refreshes cache
            for data consistency
        """
        # Validate tags exist if provided
        if update_data.tag_ids is not None:
            await self._validate_tags_exist(update_data.tag_ids)
            # Update tags separately
            await self._update_task_tags(object_id, update_data.tag_ids)
            # Remove tag_ids from update_data to avoid issues in base update
            update_data_dict = update_data.model_dump(exclude_unset=True)
            update_data_dict.pop('tag_ids', None)
            update_data = UpdateTaskSchema(**update_data_dict)

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

        Args:
            object_id: Task identifier to delete

        Note:
            Ensures proper cleanup of media files and cache
            invalidation to prevent orphaned data
        """
        # Clean up associated media files
        await self.media_service.delete_all_by_owner(
            domain=OwnerType.TASK, owner_id=object_id
        )
        # Delete task from database
        await super().delete_object(object_id=object_id)
        # Refresh cache after deletion
        await self._refresh_cache()

    # Cache management methods
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
