"""Tag services.

Provides business logic layer for category operations, including:
- CRUD operations
- media cleanup on deletion

This service acts as the orchestration layer between repositories,
media services, and API schemas.
"""

from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.models.files import OwnerType
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.tag import TagRepository
from pomodoro.task.schemas.tag import ResponseTagSchema


class TagService(CRUDService[ResponseTagSchema]):
    """Service layer for tag-related operations.

    Extends the base CRUD service with category-specific business logic:
    - media cleanup on deletion
    """

    def __init__(
        self,
        tag_repo: TagRepository,
        media_service: MediaService,
    ) -> None:
        """Initialize tag service with required dependencies.

        Args:
            tag_repo: Repository for category database operations
            media_service: Media service for associated file cleanup
        """
        self.media_service = media_service
        super().__init__(
            repository=tag_repo,
            response_schema=ResponseTagSchema,
        )

    # ------------------------------------------------------------------
    # Deletion logic
    # ------------------------------------------------------------------

    async def delete_object(self, object_id: int) -> None:
        """Delete tag and clean up associated media files.

        Args:
            object_id: Tag identifier to delete
        """
        await self.media_service.delete_all_by_owner(
            domain=OwnerType.TAG,
            owner_id=object_id,
        )
        await super().delete_object(object_id)
