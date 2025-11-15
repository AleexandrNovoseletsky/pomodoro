"""Сервисы медиа."""

import uuid

from fastapi import UploadFile
from pydantic import ValidationError

from pomodoro.core.exceptions.validation import InvalidCreateFileData
from pomodoro.core.services.base_crud import CRUDService
from pomodoro.core.settings import Settings
from pomodoro.media.repositories.media import MediaRepository
from pomodoro.media.schemas.media import CreateFileSchema, ResponseFileSchema
from pomodoro.media.storage.minio import S3Storage
from pomodoro.user.models.users import UserProfile

settings = Settings()


class MediaService(CRUDService):
    """Сервис медиа."""

    def __init__(self, media_repo: MediaRepository):
        """нициализируем сервис."""
        super().__init__(
            repository=media_repo, response_schema=ResponseFileSchema
        )

    async def upload_file(
            self,
            file: UploadFile,
            current_user: UserProfile,
            domain: str,
            ) -> str:
        """Загрузка файла в хранилище и сохранение в БД."""
        try:
            # Валидируем файл
            key = f"{domain}/{uuid.uuid4()}-{file.filename}"
            file_data = CreateFileSchema(
                owner_type=domain,
                author_id=current_user.id,
                mime=file.content_type,
                size=file.size,
                key=key,
            )
        except ValidationError as e:
            raise InvalidCreateFileData(exc=e) from e

        # Загружаем файл в S3
        storage = S3Storage()
        await storage.upload(key=key, file=file)

        # Записываем в БД
        return await super().create_object_with_author(
            object_data=file_data, current_user=current_user
        )

    async def delete_file(self, file_id: int):
        """Удаления файла из хранилища и БД."""
        # Полуяаем файл из БД
        file = await super().get_one_object(object_id=file_id)

        # Удаляем файл из хранилища
        storage = S3Storage()
        await storage.delete(key=file.key)

        # Удаляем файл из БД
        return await super().delete_object(object_id=file_id)
