"""Сервисы медиа."""

import asyncio
import uuid

import magic
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

    repository = MediaRepository

    def __init__(self, media_repo: MediaRepository):
        """нициализируем сервис."""
        self.storage = S3Storage()
        super().__init__(
            repository=media_repo, response_schema=ResponseFileSchema
        )

    async def get_presigned_url(self, file_id: int) -> str:
        file = await super().get_one_object(object_id=file_id)
        return await self.storage.generate_presigned_url(
            key=file.key,
            )

    async def get_by_owner(
            self, domain: OwnerType, owner_id: int
            ) -> list[ResponseFileSchema]:
        """Отдаёт все файлы ресурса."""
        files = await self.repository.get_by_owner(
            owner_type=domain, owner_id=owner_id
            )
        files_to_schema = [
            ResponseFileSchema.model_validate(file) for file in files
            ]
        return files_to_schema

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
            # Проверяем настоящий тип файла
            header = await file.read(2048)
            mime = magic.from_buffer(header, mime=True)
            # возвращаем позицию в начало файла
            await file.seek(0)
            file_data = CreateFileSchema(
                owner_type=domain,
                owner_id=owner_id,
                author_id=current_user.id,
                mime=mime,
                size=file.size,
                key=key,
            )
        except ValidationError as e:
            raise InvalidCreateFileData(exc=e) from e

        # Проверяем что существует owner с указанным типом и ID
        await self._verify_owner_exists(owner_type=domain, owner_id=owner_id)

        # Загружаем файл в S3
        await self.storage.upload(key=key, file=file, real_mime=mime)

        # Записываем в БД
        return await super().create_object_with_author(
            object_data=file_data, current_user=current_user
        )

    async def set_primary(self, file_id: int) -> ResponseFileSchema:
        file: ResponseFileSchema = await super().get_one_object(
            object_id=file_id
            )
        file_key = file.key
        owner_type, owner_id = await self._get_owner_and_owner_id_by_key(
            key=file_key
            )
        return await self.repository.set_primary(
            file_id=file_id, owner_type=owner_type, owner_id=owner_id
            )

    async def delete_file(self, file_id: int) -> None:
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
        sem = asyncio.Semaphore(10)

        async def _del(f):
            async with sem:
                await self.storage.delete(f.key)
                await self.repository.delete_object(object_id=f.id)
        await asyncio.gather(*[_del(f) for f in files])

    async def _verify_owner_exists(
            self, owner_type: str, owner_id: int
            ) -> None:
        owner_type_enum = OwnerType(owner_type)

        if owner_type_enum == OwnerType.TASK:
            repo = TaskRepository(sessionmaker=self.repository.sessionmaker)
            if await repo.get_object(owner_id) is None:
                raise ObjectNotFoundError(owner_id)

        elif owner_type_enum == OwnerType.CATEGORY:
            repo = CategoryRepository(
                sessionmaker=self.repository.sessionmaker
                )
            if await repo.get_object(owner_id) is None:
                raise ObjectNotFoundError(owner_id)

        elif owner_type_enum == OwnerType.USER:
            repo = UserRepository(sessionmaker=self.repository.sessionmaker)
            if await repo.get_object(owner_id) is None:
                raise ObjectNotFoundError(owner_id)

    async def _get_owner_and_owner_id_by_key(
            self, key: str
            ) -> tuple[str, int]:
        split_key = key.split(sep="/")
        return split_key[0], int(split_key[1])
