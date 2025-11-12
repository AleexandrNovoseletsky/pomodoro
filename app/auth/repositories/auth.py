from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models.oauth_accaunts import OAuthAccount
from app.core.repositories.base_crud import CRUDRepository


class AuthRepository(CRUDRepository):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session=db_session, orm_model=OAuthAccount)

    async def get_by_provider_user(
        self, provider: str, provider_user_id: str
    ) -> OAuthAccount | None:
        query = (
            select(OAuthAccount)
            .where(OAuthAccount.provider == provider)
            .where(OAuthAccount.provider_user_id == provider_user_id)
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
