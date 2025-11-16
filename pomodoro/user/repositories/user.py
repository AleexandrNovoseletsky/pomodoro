"""Репозитории пользователей."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.user.models.users import UserProfile


class UserRepository(CRUDRepository):
    """Репозиторий пользователей. Унаследован от базового репозитория."""

    def __init__(self, sessionmaker: async_sessionmaker):
        """Инициализируем репозиторий."""
        super().__init__(sessionmaker=sessionmaker, orm_model=UserProfile)

    async def get_by_phone(self, user_phone: str) -> UserProfile | None:
        """Находит пользователя по номеру телефона."""
        query = select(UserProfile).where(UserProfile.phone == user_phone)
        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def update_object(self, object_id, update_data):
        """Изминение данных о пользователе."""
        # Если меняется телефон, он становится не верифицированным.
        if "phone" in update_data.model_dump(exclude_unset=True):
            update_data.phone_verified = False
        # Если меняется почта, она становится не верифицированной.
        if "email" in update_data.model_dump(exclude_unset=True):
            update_data.email_verified = False
        return await super().update_object(object_id, update_data)
