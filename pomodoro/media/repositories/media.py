"""Репозитории медиа."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.media.models.files import Files, OwnerType


class MediaRepository(CRUDRepository):
    """Репозиторий медиа."""

    def __init__(self, db_session: AsyncSession):
        """Инициализируем репозиторий."""
        super().__init__(db_session, Files)

    async def get_by_owner(
            self, owner_type: OwnerType, owner_id: int
            ) -> list[Files]:
        """Получение всех файлов по owner_id."""
        query = select(Files).where(
            Files.owner_type == owner_type,
            Files.owner_id == owner_id,
            )
        result = await self.db_session.execute(query)
        return result.scalars().all()
