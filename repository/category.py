from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from database import Categories, Tasks, get_db_session
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
    ) -> Categories:
        # Преобразуем Pydantic модель в словарь, исключая значения,
        # которые не были переданы
        update_dict = update_data.model_dump(exclude_unset=True)
        if not update_dict:
            return self.get_category(category_id)
        query = update(Categories).where(
            Categories.id == category_id
        ).values(**update_dict)
        with self.db_session() as session:
            session.execute(query)
            session.commit()
            category = self.get_category(category_id)
            return category

    def delete_category(self, category_id) -> None:
        query = delete(Categories).where(Categories.id == category_id)
        with self.db_session() as session:
            session.execute(query)
            session.commit()
