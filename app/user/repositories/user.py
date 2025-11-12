from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.repositories.base_crud import CRUDRepository
from app.user.models.users import UserProfile


class UserRepository(CRUDRepository):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, UserProfile)

    async def get_by_phone(self, user_phone: str) -> UserProfile | None:
        query = select(UserProfile).where(UserProfile.phone == user_phone)
        result = await self.db_session.execute(query)
        user = result.scalar_one_or_none()
        return user

    async def update_object(self, object_id, update_data):
        if "phone" in update_data.model_dump(exclude_unset=True):
            setattr(update_data, "phone_verified", False)
        return await super().update_object(object_id, update_data)
