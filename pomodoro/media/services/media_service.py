"""Сервисы медиа."""

import asyncio
import io
import sys
import uuid
from pathlib import Path

import magic
from fastapi import UploadFile
from pydantic import ValidationError

from pomodoro.core.exceptions.object_not_found import ObjectNotFoundError
from pomodoro.core.exceptions.validation import InvalidCreateFileData
from pomodoro.core.services.base_crud import CRUDService
from pomodoro.core.settings import Settings
from pomodoro.media.converters.image_converters import convert_to_webp, resize_image
from pomodoro.media.models.files import OwnerType, Files, AllowedMimeTypes, Variants
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
            domain: OwnerType,
            owner_id: int,
            ) -> ResponseFileSchema:
        """Загрузка файла в хранилище и сохранение в БД."""
        key: str = f"{domain}/{owner_id}/{uuid.uuid4()}-{file.filename}"
        mime: AllowedMimeTypes = await self._get_real_mime(file=file)
        try:
            # Валидируем файл
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

    async def upload_image(
            self,
            image: UploadFile,
            current_user: UserProfile,
            domain: OwnerType,
            owner_id: int,
    ) -> list[ResponseFileSchema]:
        filename = Path(image.filename).stem
        mime = await self._get_real_mime(file=image)
        await self._verify_owner_exists(owner_type=domain, owner_id=owner_id)

        # -- Generate keys --
        key_params = {
            "domain": domain,
            "owner_id": owner_id,
            "filename": filename
        }
        original_key = await self._get_key(
            **key_params,
            variant=Variants.ORIGINAL
        )
        small_key = await self._get_key(
            **key_params,
            variant=Variants.SMALL
        )
        thumb_key = await self._get_key(
            **key_params,
            variant=Variants.THUMB
        )

        # -- Generate files --
        original_image_bytes: bytes = await image.read()
        original_webp = await convert_to_webp(image=original_image_bytes)
        small_webp = await resize_image(
            image=original_webp, width=settings.SMALL_WIDTH
        )
        thumb_webp = await resize_image(
            image=original_webp, width=settings.THUMB_WIDTH
        )
        files: dict[str, io.BytesIO | UploadFile] = {
            original_key: original_webp,
            small_key: small_webp,
            thumb_key: thumb_webp
        }

        # -- Upload files --
        await self._upload_variants(files=files, mime=mime)

        # -- Recording to DB --
        try:
            # -- Generate file schemas --
            author_id = current_user.id
            schemas_data = {
                "owner_type": domain,
                "owner_id": owner_id,
                "author_id": author_id,
                "mime": mime,
            }
            original_schema = CreateFileSchema(
                **schemas_data,
                size=sys.getsizeof(original_webp),
                key=original_key,
                variant=Variants.ORIGINAL,

            )
            small_schema = CreateFileSchema(
                **schemas_data,
                size=sys.getsizeof(small_webp),
                key=small_key,
                variant=Variants.SMALL,
            )
            thumb_schema = CreateFileSchema(
                **schemas_data,
                size=sys.getsizeof(thumb_webp),
                key=thumb_key,
                variant=Variants.THUMB,
            )

            db_files = [
                await super().create_object_with_author(
                    object_data=original_schema,
                    current_user=current_user,

                ),
                await super().create_object_with_author(
                    object_data=small_schema, current_user=current_user
                ),
                await super().create_object_with_author(
                    object_data=thumb_schema, current_user=current_user
                )
            ]
            return db_files

        # -- Rollback upload files
        except Exception:
            await self.storage.delete(original_key)
            await self.storage.delete(small_key)
            await self.storage.delete(thumb_key)
            raise


    async def set_primary(self, file_id: int) -> ResponseFileSchema:
        file: ResponseFileSchema = await super().get_one_object(
            object_id=file_id
            )
        file_key = file.key
        owner_type, owner_id = await self._get_owner_and_owner_id_by_key(
            key=file_key
            )
        file: Files = await self.repository.set_primary(
            file_id=file_id, owner_type=owner_type, owner_id=owner_id
            )
        return ResponseFileSchema.model_validate(file)

    async def delete_file(self, file_id: int) -> None:
        """Удаления файла из хранилища и БД."""
        # Получаем файл из БД
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
    async def _upload_variants(
            self,
            files: dict[str, UploadFile | bytes],
            mime: AllowedMimeTypes
    ) -> None:
        for key, file in files.items():
            await self.storage.upload(key=key, file=file, mime=mime)


    @staticmethod
    async def _get_owner_and_owner_id_by_key(key: str) -> tuple[str, int]:
        split_key = key.split(sep="/")
        return split_key[0], int(split_key[1])

    @staticmethod
    async def _get_real_mime(file: UploadFile) -> AllowedMimeTypes:
        header = await file.read(2048)
        real_mime = magic.from_buffer(header, mime=True)
        await file.seek(0)
        try:
            return AllowedMimeTypes(real_mime)
        except ValueError:
            raise ValueError(f"Недопустимый тип файла {real_mime}.")

    @staticmethod
    async def _get_key(
            domain: OwnerType,
            owner_id: int,
            filename: str,
            variant: str | None
    ) -> str:
        variant = f"-{variant}"
        return f"{domain}/{owner_id}/{uuid.uuid4()}{variant}-{filename}.webp"
