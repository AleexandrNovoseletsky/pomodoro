from sqlalchemy import select
from sqlalchemy.orm import Session

from models import UserProfile
from repositories.crud import CRUDRepository


class UserRepository(CRUDRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session, UserProfile)

    async def get_by_phone(self, user_phone: str) -> UserProfile:
        query = select(UserProfile).where(UserProfile.phone == user_phone)
        user = self.db_session.execute(query).scalar_one_or_none()
        return user
