"""Category services.

Provides business logic layer for category operations with media
integration. Extends base CRUD service with category-specific
functionality and media cleanup.
"""

from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.models.files import OwnerType
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.schemas.category import ResponseCategorySchema


class CategoryService(CRUDService):
    """Category service inheriting from base CRUD service.

    Extends base CRUD operations with category-specific business logic
    including media file management and cleanup during deletion.

    Attributes:     media_service: Media service instance for file
    operations     repository: Category repository for data access
    response_schema: Response schema for data serialization
    """

    def __init__(
        self,
        category_repo: CategoryRepository,
        media_service: MediaService,
    ):
        """Initialize category service with dependencies.

        Args:     category_repo: Category repository for data operations
        media_service: Media service for file management
        """
        self.media_service = media_service
        super().__init__(
            repository=category_repo, response_schema=ResponseCategorySchema
        )

    async def delete_object(self, object_id):
        """Delete category with associated media cleanup.

        Performs complete category deletion including removal of all
        associated media files before deleting the category record.

        Args:     object_id: Category identifier to delete

        Returns:     Result of base delete operation

        Note:     Ensures proper cleanup of media files to prevent
        orphaned     files in storage when categories are deleted.
        """
        # Clean up associated media files
        await self.media_service.delete_all_by_owner(
            domain=OwnerType.CATEGORY, owner_id=object_id
        )
        return await super().delete_object(object_id)
