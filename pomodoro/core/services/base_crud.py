"""Базовый класс для всех сервисов. CRUD операции."""
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from pomodoro.core.exceptions.integrity import IntegrityDBError
from pomodoro.core.exceptions.object_not_found import ObjectNotFoundError
from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.user.models.users import UserProfile


class CRUDService:
    """Базовый сервис поверх CRUDRepository.

    Сервисы преобразуют ORM-объекты в Pydantic-схемы (`response_schema`).
    Методики обработки ошибок используют исключения из
    `pomodoro.core.exceptions`.
    """

    def __init__(
        self, repository: CRUDRepository, response_schema: type[BaseModel]
    ):
        """Инициализируем базовый репозиторий."""
        self.repository = repository
        self.response_schema = response_schema

    async def get_one_object(self, object_id: int):
        """Получить один объект и вернуть Pydantic-валидацию.

        Бросает ObjectNotFoundError если объект не найден.
        """
        db_object = await self.repository.get_object(object_id=object_id)
        if db_object is None:
            raise ObjectNotFoundError(object_id=object_id)
        return self.response_schema.model_validate(obj=db_object)

    async def get_all_objects(self):
        """Получить список объектов и вернуть список Pydantic-схем."""
        db_objects = await self.repository.get_all_objects()
        object_schema = [
            self.response_schema.model_validate(row) for row in db_objects
        ]
        return object_schema

    async def create_object(self, object_data: BaseModel):
        """Создать объект через репозиторий и вернуть Pydantic-экземпляр."""
        try:
            new_object = await self.repository.create_object(data=object_data)
        except IntegrityError as e:
            raise IntegrityDBError(exc=e) from e
        return self.response_schema.model_validate(obj=new_object)

    async def create_object_with_author(
        self,
        object_data: BaseModel,
        current_user: UserProfile,
    ):
        """Создать объект и автоматически добавить поле author_id."""
        try:
            data_dict = object_data.model_dump()
            data_dict["author_id"] = current_user.id
            # Создаём новый экземпляр той же Pydantic-схемы
            new_input = object_data.__class__(**data_dict)
            new_object = await self.repository.create_object(data=new_input)
        except IntegrityError as e:
            raise IntegrityDBError(exc=e) from e
        return self.response_schema.model_validate(obj=new_object)

    async def update_object(self, object_id: int, update_data: BaseModel):
        """Обновить объект и вернуть Pydantic-валидированный результат."""
        try:
            updated_object_or_none = await self.repository.update_object(
                object_id=object_id, update_data=update_data
            )
        except IntegrityError as e:
            raise IntegrityDBError(exc=e) from e
        if updated_object_or_none is None:
            raise ObjectNotFoundError(object_id=object_id)
        return self.response_schema.model_validate(obj=updated_object_or_none)

    async def delete_object(self, object_id: int) -> None:
        """Удалить объект; если его нет — бросить ObjectNotFoundError."""
        deleted = await self.repository.delete_object(object_id=object_id)
        if not deleted:
            raise ObjectNotFoundError(object_id=object_id)
        return None
