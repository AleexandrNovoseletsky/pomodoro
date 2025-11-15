"""Сервисы медиа."""

import uuid

from fastapi import UploadFile
from pydantic import ValidationError

from pomodoro.core.exceptions.object_not_found import ObjectNotFoundError
from pomodoro.core.exceptions.validation import InvalidCreateFileData
from pomodoro.core.services.base_crud import CRUDService
from pomodoro.core.settings import Settings
from pomodoro.media.models.files import OwnerType
from pomodoro.media.repositories.media import MediaRepository
from pomodoro.media.schemas.media import CreateFileSchema, ResponseFileSchema
from pomodoro.media.storage.minio import S3Storage
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.user.models.users import UserProfile
from pomodoro.user.repositories.user import UserRepository

settings = Settings()


class MediaService(CRUDService):
    """Сервис медиа."""

    def __init__(self, media_repo: MediaRepository):
        """нициализируем сервис."""
        self.storage = S3Storage()
        super().__init__(
            repository=media_repo, response_schema=ResponseFileSchema
        )

    async def upload_file(
            self,
            file: UploadFile,
            current_user: UserProfile,
            domain: str,
            owner_id: int,
            ) -> ResponseFileSchema:
        """Загрузка файла в хранилище и сохранение в БД."""
        try:
            # Валидируем файл
            key = f"{domain}/{owner_id}/{uuid.uuid4()}-{file.filename}"
            file_data = CreateFileSchema(
                owner_type=domain,
                owner_id=owner_id,
                author_id=current_user.id,
                mime=file.content_type,
                size=file.size,
                key=key,
            )
        except ValidationError as e:
            raise InvalidCreateFileData(exc=e) from e

        # Проверяем что существует owner с указанным типом и ID
        await self._verify_owner_exists(owner_type=domain, owner_id=owner_id)

        # Загружаем файл в S3
        await self.storage.upload(key=key, file=file)

        # Записываем в БД
        return await super().create_object_with_author(
            object_data=file_data, current_user=current_user
        )

    async def delete_file(self, file_id: int):
        """Удаления файла из хранилища и БД."""
        # Полуяаем файл из БД
        file = await super().get_one_object(object_id=file_id)

        # Удаляем файл из хранилища
        await self.storage.delete(key=file.key)

        # Удаляем файл из БД
        return await super().delete_object(object_id=file_id)

    async def delete_all_by_owner(
            self, owner_type: OwnerType, owner_id: int
            ) -> None:
        files = await self.repository.get_by_owner(
            owner_type=owner_type, owner_id=owner_id
            )
        for file in files:
            await self.storage.delete(file.key)
            await self.repository.delete_object(object_id=file.id)

    async def _verify_owner_exists(self, owner_type: str, owner_id: int):
        owner_type_enum = OwnerType(owner_type)

        if owner_type_enum == OwnerType.TASK:
            repo = TaskRepository(db_session=self.repository.db_session)
            if await repo.get_object(owner_id) is None:
                raise ObjectNotFoundError(owner_id)

        elif owner_type_enum == OwnerType.CATEGORY:
            repo = CategoryRepository(db_session=self.repository.db_session)
            if await repo.get_object(owner_id) is None:
                raise ObjectNotFoundError(owner_id)

        elif owner_type_enum == OwnerType.USER:
            repo = UserRepository(db_session=self.repository.db_session)
            if await repo.get_object(owner_id) is None:
                raise ObjectNotFoundError(owner_id)
