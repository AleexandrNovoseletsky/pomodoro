from typing import Type, Optional

from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.orm import Session, DeclarativeBase


class CRUDRepository:
    def __init__(self, db_session: Session, orm_model: Type[DeclarativeBase]):
        self.db_session = db_session
        self.orm_model = orm_model

    async def create_object(self, data: BaseModel):
        obj = self.orm_model(**data.model_dump())
        self.db_session.add(obj)
        self.db_session.commit()
        self.db_session.refresh(obj)
        return obj

    async def get_object(self, object_id: int):
        return self.db_session.execute(
            select(self.orm_model).where(self.orm_model.id == object_id)
        ).scalar_one_or_none()

    async def get_all_objects(self):
        return self.db_session.execute(select(self.orm_model)).scalars().all()

    async def update_object(
        self, object_id: int, update_data: BaseModel
    ) -> Optional[DeclarativeBase]:
        obj = self.db_session.execute(
            select(self.orm_model).where(self.orm_model.id == object_id)
        ).scalar_one_or_none()

        if obj is None:
            return None

        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(obj, key, value)

        self.db_session.commit()
        self.db_session.refresh(obj)
        return obj

    async def delete_object(self, object_id: int) -> bool:
        result = self.db_session.execute(
            delete(self.orm_model).where(self.orm_model.id == object_id)
        )
        self.db_session.commit()
        return result.rowcount > 0
