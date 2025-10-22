from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database import Categories
from schemas.Category import CreateCategorySchema, UpdateCategorySchema


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

    def create_category(self, category: CreateCategorySchema) -> Categories:
        category_orm = Categories(
            name=category.name
        )
        with self.db_session() as session:
            session.add(category_orm)
            session.commit()
            session.refresh(category_orm)
            return category_orm

    def update_category(
            self,
            category_id: int,
            update_data: UpdateCategorySchema
    ) -> Categories | None:
        # Преобразуем Pydantic модель в словарь, исключая значения,
        # которые не были переданы
        query = select(Categories).where(Categories.id == category_id)

        with self.db_session() as session:
            category = session.execute(query).scalar_one_or_none()
            if category is None:
                return None
            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(category, key, value)
            session.commit()
            session.refresh(category)
            return category

    def delete_category(self, category_id) -> bool:
        query = delete(Categories).where(Categories.id == category_id)
        with self.db_session() as session:
            result = session.execute(query)
            session.commit()
            return result.rowcount > 0
