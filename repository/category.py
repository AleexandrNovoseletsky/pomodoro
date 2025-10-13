from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database import Categories, Tasks, get_db_session


class CategoryRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_category(self, category_id: int) -> Categories | None:
        query = select(Categories).where(Categories.id == category_id)
        with self.db_session() as session:
            return session.execute(query).scalars().one_or_none()

    def get_categories(self) -> list[Categories]:
        query = select(Categories)
        with self.db_session() as session:
            categories = session.execute(query).scalars().all()
            return categories

    def create_category(self, category: Categories) -> Categories:
        with self.db_session() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category

    def delete_category(self, category_id) -> None:
        query = delete(Categories).where(Categories.id == category_id)
        with self.db_session() as session:
            session.execute(query)
            session.commit()
