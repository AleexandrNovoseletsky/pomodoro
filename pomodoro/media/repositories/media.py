"""Media repositories."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.media.models.files import Files, OwnerType
from pomodoro.media.schemas.media import SetPrimarySchema


class MediaRepository(CRUDRepository):
    """Media repository."""

    def __init__(self, sessionmaker: async_sessionmaker):
        """Initializing repository.

        Args:     sessionmaker: Async session maker
        """
        super().__init__(sessionmaker=sessionmaker, orm_model=Files)

    async def get_by_owner(
        self, domain: OwnerType, owner_id: int
    ) -> list[Files]:
        """Getting all files by owner_id.

        Args:     domain: CThe domain to which the file belongs. Example
        Task.     owner_id: The resource ID to which the files belong.

        Returns:     List of files.
        """
        async with self.sessionmaker() as session:
            query = select(Files).where(
                Files.owner_type == domain,
                Files.owner_id == owner_id,
            )
            result = await session.execute(query)
            return result.scalars().all()

    async def set_primary(
        self, file_id: int, domain: OwnerType, owner_id: int
    ) -> Files:
        """Set one file is primary.

        Args:     file_id: The file ID that is set as is_primary.
        domain: The domain to which the file belongs. Example Task.
        owner_id: The resource ID to which the file belongs.

        Returns:     ORM file object.
        """
        # Set all is_primary resources to False
        files = await self.get_by_owner(domain=domain, owner_id=owner_id)
        for file in files:
            file.is_primary = False
        # Setting the specified file to True
        update_data = SetPrimarySchema(is_primary=True)
        return await super().update_object(
            object_id=file_id, update_data=update_data
        )
