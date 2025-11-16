"""Репозитории авторизации."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.auth.models.oauth_accaunts import OAuthAccount
from pomodoro.core.repositories.base_crud import CRUDRepository


class AuthRepository(CRUDRepository):
    """Репозиторий авторизации."""

    def __init__(self, sessionmaker: async_sessionmaker):
        """Инициализации репозитория."""
        super().__init__(sessionmaker=sessionmaker, orm_model=OAuthAccount)

    async def get_by_provider_user(
        self, provider: str, provider_user_id: str
    ) -> OAuthAccount | None:
        """Поиск вненего пользователя от провайдера."""
        query = (
            select(OAuthAccount)
            .where(OAuthAccount.provider == provider)
            .where(OAuthAccount.provider_user_id == provider_user_id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
