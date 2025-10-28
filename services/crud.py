from typing import List

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

from exceptions.object_not_found import ObjectNotFoundError
from repositories.crud import CRUDRepository


class CRUDService:
    def __init__(
            self,
            repository: CRUDRepository,
            response_schema: BaseModel,
    ):
        self.repository = repository
        self.response_schema = response_schema

    async def get_one_object(self, object_id: int) -> BaseModel:
        return await self.repository.get_object(object_id=object_id)

    async def get_all_objects(self) -> List[BaseModel]:
        db_objects = await self.repository.get_all_objects()
        object_schema = [
            self.response_schema.model_validate(row)
            for row in db_objects
        ]
        return object_schema

    async def create_object(
            self,
            object_data: BaseModel
    ) -> DeclarativeBase:
        new_object = await self.repository.create_object(
            data=object_data
        )
        return new_object

    async def update_object(
            self,
            object_id: int,
            update_data: BaseModel

    ) -> DeclarativeBase:
        updated_object_or_none = await self.repository.update_object(
            object_id=object_id, update_data=update_data
        )
        if updated_object_or_none is None:
            raise ObjectNotFoundError(object_id=object_id)
        return updated_object_or_none

    async def delete_object(self, object_id: int) -> None:
        deleted = await self.repository.delete_object(object_id)
        if not deleted:
            raise ObjectNotFoundError(object_id=object_id)
        return None
