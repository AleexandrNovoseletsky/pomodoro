"""Репозитории медиа."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.media.models.files import Files, OwnerType
from pomodoro.media.schemas.media import SetPrimarySchema


class MediaRepository(CRUDRepository):
    """Репозиторий медиа."""

    def __init__(self, sessionmaker: async_sessionmaker):
        """Инициализируем репозиторий."""
        super().__init__(sessionmaker=sessionmaker, orm_model=Files)

    async def get_by_owner(
            self, owner_type: OwnerType, owner_id: int
            ) -> list[Files]:
        """Получение всех файлов по owner_id."""
        async with self.sessionmaker() as session:
            query = select(Files).where(
                Files.owner_type == owner_type,
                Files.owner_id == owner_id,
                )
            result = await session.execute(query)
            return result.scalars().all()

    async def set_primary(
            self, file_id: int, owner_type: OwnerType, owner_id: int
            ) -> Files:
        # Устанавливаем все is_primary ресурса в False
        files = await self.get_by_owner(
            owner_type=owner_type, owner_id=owner_id
            )
        for file in files:
            file.is_primary = False
        # Устанавдиваем указаный файл в True
        update_data = SetPrimarySchema(is_primary=True)
        return await super().update_object(
            object_id=file_id, update_data=update_data
            )
