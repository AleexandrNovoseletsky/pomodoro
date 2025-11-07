from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from custom_exceptions.integrity import IntegrityDBError
from custom_exceptions.object_not_found import ObjectNotFoundError
from repositories.base_crud import CRUDRepository


class CRUDService:
    response_schema = None
    def __init__(self, repository: CRUDRepository):
        self.repository = repository
        if self.response_schema is None:
            self.response_schema = self._autodetect_schema()

    def _autodetect_schema(self):
        """
        ищем схему по имени ORM-модели
        Example: UserProfile -> ResponseUserProfileSchema
        """
        orm_name = self.repository.orm_model.__name__
        schema_name = f'Response{orm_name}Schema'

        from schemas import __dict__ as schemas_namespace

        schema_cls = schemas_namespace.get(schema_name)
        if schema_cls is None:
            print(f"{schema_name=}  {schema_cls=}")
            raise RuntimeError(
                f'Схема {schema_name} не найдена. '
                f'Либо создай {schema_name}, либо явно укажи response_schema в сервисе.'
            )
        return schema_cls

    async def get_one_object(self, object_id: int):
        db_object = await self.repository.get_object(object_id=object_id)
        if db_object is None:
            raise ObjectNotFoundError(object_id=object_id)
        return self.response_schema.model_validate(obj=db_object)

    async def get_all_objects(self):
        db_objects = await self.repository.get_all_objects()
        object_schema = [self.response_schema.model_validate(row) for row in db_objects]
        return object_schema

    async def create_object(self, object_data: BaseModel):
        try:
            new_object = await self.repository.create_object(data=object_data)
        except IntegrityError as e:
            raise IntegrityDBError(exc=e)
        return self.response_schema.model_validate(obj=new_object)

    async def update_object(self, object_id: int, update_data: BaseModel):
        try:
            updated_object_or_none = await self.repository.update_object(
                object_id=object_id, update_data=update_data
            )
        except IntegrityError as e:
            raise IntegrityDBError(exc=e)
        if updated_object_or_none is None:
            raise ObjectNotFoundError(object_id=object_id)
        return self.response_schema.model_validate(obj=updated_object_or_none)

    async def delete_object(self, object_id: int) -> None:
        deleted = await self.repository.delete_object(object_id=object_id)
        if not deleted:
            raise ObjectNotFoundError(object_id=object_id)
        return None
