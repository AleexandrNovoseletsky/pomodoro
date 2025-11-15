"""Репозитории медиа."""

from sqlalchemy.ext.asyncio import AsyncSession

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.media.models.files import Files


class MediaRepository(CRUDRepository):
    """Репозиторий медиа."""

    def __init__(self, db_session: AsyncSession):
        """Инициализируем репозиторий."""
        super().__init__(db_session, Files)
