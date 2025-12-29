"""Category services.

Provides business logic layer for category operations, including:
- CRUD operations
- hierarchical category tree construction
- subtree extraction
- media cleanup on deletion

This service acts as the orchestration layer between repositories,
media services, and API schemas.
"""

from collections import defaultdict
from collections.abc import Iterable

from pomodoro.core.exceptions.object_not_found import ObjectNotFoundError
from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.models.files import OwnerType
from pomodoro.media.services.media_service import MediaService
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.schemas.category import (
    CategoryTreeSchema,
    ResponseCategorySchema,
)


class CategoryService(CRUDService[ResponseCategorySchema]):
    """Service layer for category-related operations.

    Extends the base CRUD service with category-specific business logic:
    - media cleanup on deletion
    - hierarchical category tree generation
    - subtree extraction
    """

    def __init__(
        self,
        category_repo: CategoryRepository,
        media_service: MediaService,
    ) -> None:
        """Initialize category service with required dependencies.

        Args:
            category_repo: Repository for category database operations
            media_service: Media service for associated file cleanup
        """
        self.media_service = media_service
        super().__init__(
            repository=category_repo,
            response_schema=ResponseCategorySchema,
        )

    # ------------------------------------------------------------------
    # Deletion logic
    # ------------------------------------------------------------------

    async def delete_object(self, object_id: int) -> None:
        """Delete category and clean up associated media files.

        Important:
            This method does NOT reassign tasks.
            All tasks referencing this category must be handled explicitly
            before deletion.

        Args:
            object_id: Category identifier to delete
        """
        await self.media_service.delete_all_by_owner(
            domain=OwnerType.CATEGORY,
            owner_id=object_id,
        )
        await super().delete_object(object_id)

    # ------------------------------------------------------------------
    # Tree logic (public API)
    # ------------------------------------------------------------------

    async def get_tree(self) -> list[CategoryTreeSchema]:
        """Return full hierarchical category tree.

        Returns:
            List of root categories with recursively populated children
        """
        categories = await self.repository.get_all_objects()
        return self._build_tree(categories)

    async def get_subtree(self, category_id: int) -> CategoryTreeSchema:
        """Return subtree for a specific category.

        Args:
            category_id: Root category identifier

        Returns:
            CategoryTreeSchema representing the subtree root

        Raises:
            NotFoundError: If category does not exist
        """
        categories = await self.repository.get_all_objects()

        category_map = {category.id: category for category in categories}
        root = category_map.get(category_id)

        if root is None:
            raise ObjectNotFoundError(object_id=category_id)

        return self._build_subtree(root, categories)

    # ------------------------------------------------------------------
    # Tree logic (internal helpers)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_tree(
        categories: Iterable,
    ) -> list[CategoryTreeSchema]:
        """Build full category tree from flat category list.

        Args:
            categories: Iterable of Category ORM objects

        Returns:
            List of root CategoryTreeSchema objects
        """
        children_map: dict[int | None, list] = defaultdict(list)

        for category in categories:
            children_map[category.parent_id].append(category)

        def build_node(category) -> CategoryTreeSchema:
            return CategoryTreeSchema(
                id=category.id,
                name=category.name,
                is_active=category.is_active,
                children=[
                    build_node(child)
                    for child in children_map.get(category.id, [])
                ],
            )

        roots = children_map.get(None, [])

        return [build_node(root) for root in roots]

    @staticmethod
    def _build_subtree(
        root,
        categories: Iterable,
    ) -> CategoryTreeSchema:
        """Build subtree starting from a specific root category.

        Args:
            root: Root Category ORM object
            categories: Iterable of all Category ORM objects

        Returns:
            CategoryTreeSchema subtree
        """
        children_map: dict[int, list] = defaultdict(list)

        for category in categories:
            if category.parent_id is not None:
                children_map[category.parent_id].append(category)

        def build_node(category) -> CategoryTreeSchema:
            return CategoryTreeSchema(
                id=category.id,
                name=category.name,
                is_active=category.is_active,
                children=[
                    build_node(child)
                    for child in children_map.get(category.id, [])
                ],
            )

        return build_node(root)
