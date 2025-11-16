"""Media service for file and image management."""

import asyncio
import logging

import uuid
from io import BytesIO

from fastapi import UploadFile

from pomodoro.core.exceptions.object_not_found import (
    ObjectNotFoundError,
)
from pomodoro.core.services.base_crud import CRUDService
from pomodoro.core.settings import Settings
from pomodoro.media.models.files import OwnerType
from pomodoro.media.repositories.media import MediaRepository
from pomodoro.media.schemas.media import ResponseFileSchema
from pomodoro.media.storage.minio import S3Storage
from pomodoro.media.utils.files import FileChecker
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.user.models.users import UserProfile
from pomodoro.user.repositories.user import UserRepository

settings = Settings()
logger = logging.getLogger(__name__)


class MediaService(CRUDService):
    """Media file management service.

    Handles file uploads (single and batch), image processing with
    variants, file deletion from storage and DB, and owner verification.
    """

    repository = MediaRepository
    _upload_semaphore = asyncio.Semaphore(5)
    _delete_semaphore = asyncio.Semaphore(10)

    def __init__(self, media_repo: MediaRepository) -> None:
        """Initialize media service with storage and repository.

        Args:
            media_repo: Media repository instance.
        """
        self.storage = S3Storage()
        super().__init__(
            repository=media_repo, response_schema=ResponseFileSchema
        )

    async def get_presigned_url(self, file_id: int) -> str:
        """Get temporary presigned URL for file download.

        Args:
            file_id: ID of the file record.

        Returns:
            Presigned URL string.

        Raises:
            ObjectNotFoundError: If file not found.
        """
        file = await super().get_one_object(object_id=file_id)
        return await self.storage.generate_presigned_url(key=file.key)

    async def get_by_owner(
        self, domain: OwnerType, owner_id: int
    ) -> list[ResponseFileSchema]:
        """Get all files for specific owner.

        Args:
            domain: Owner type (user/task/category).
            owner_id: ID of the owner.

        Returns:
            List of file schemas.
        """
        files = await self.repository.get_by_owner(
            owner_type=domain, owner_id=owner_id
        )
        return [ResponseFileSchema.model_validate(f) for f in files]

    async def upload_file(
        self,
        file: UploadFile,
        current_user: UserProfile,
        domain: OwnerType,
        owner_id: int,
    ) -> ResponseFileSchema:
        """Upload single file to storage and DB.

        Args:
            file: Uploaded file.
            current_user: User uploading the file.
            domain: Owner type.
            owner_id: ID of the owner.

        Returns:
            File schema with DB metadata.

        Raises:
            InvalidCreateFileData: If file validation fails.
            ObjectNotFoundError: If owner not found.
        """
        key = self._get_key(
            domain=domain, owner_id=owner_id, file_name=file.filename
        )

        checker = FileChecker(file=file)
        verified_file = await checker.validate_file(
            domain=domain,
            owner_id=owner_id,
            author_id=current_user.id,
            key=key,
        )

        await self._verify_owner_exists(
            owner_type=domain, owner_id=owner_id
        )

        await self.storage.upload(
            key=key, file=file, real_mime=verified_file.mime
        )

        return await super().create_object_with_author(
            object_data=verified_file, current_user=current_user
        )

    async def upload_image(
        self,
        file: UploadFile,
        current_user: UserProfile,
        domain: OwnerType,
        owner_id: int,
    ) -> list[ResponseFileSchema]:
        """Upload image with WebP variant generation.

        Generates three variants (original, small, thumb) and uploads
        them concurrently to storage.

        Args:
            file: Uploaded image file.
            current_user: User uploading the image.
            domain: Owner type.
            owner_id: ID of the owner.

        Returns:
            List of file schemas for each variant.

        Raises:
            InvalidCreateFileData: If image validation fails.
            ObjectNotFoundError: If owner not found.
        """
        file_name = file.filename

        # validate input
        checker = FileChecker(file=file)
        verified_file = await checker.validate_file(
            domain=domain,
            owner_id=owner_id,
            author_id=current_user.id,
            key="",
        )
        processed = await checker.process_image()

        await self._verify_owner_exists(
            owner_type=domain, owner_id=owner_id
        )

        # upload variants in parallel
        upload_tasks = [
            self._upload_variant(
                suffix, data, domain, owner_id, file_name
            )
            for suffix, data in [
                ("ORIGINAL", processed["original"]),
                ("SMALL", processed["small"]),
                ("THUMB", processed["thumb"]),
            ]
        ]

        upload_results = await asyncio.gather(*upload_tasks)
        db_records = await self._create_db_records(
            verified_file, current_user, upload_results
        )

        return db_records

    async def upload_files(
        self,
        files: list[UploadFile],
        current_user: UserProfile,
        domain: str,
        owner_id: int,
    ) -> list[ResponseFileSchema]:
        """Upload multiple files concurrently.

        Args:
            files: List of files to upload.
            current_user: User uploading files.
            domain: Owner type.
            owner_id: ID of the owner.

        Returns:
            List of file schemas.
        """
        tasks = [
            self._upload_with_semaphore(
                file, current_user, domain, owner_id
            )
            for file in files
        ]
        return await asyncio.gather(*tasks)

    async def set_primary(
        self, file_id: int
    ) -> ResponseFileSchema:
        """Mark file as primary for its owner.

        Args:
            file_id: ID of the file to set as primary.

        Returns:
            Updated file schema.
        """
        file: ResponseFileSchema = await super().get_one_object(
            object_id=file_id
        )
        owner_type, owner_id = self._parse_owner_from_key(file.key)
        return await self.repository.set_primary(
            file_id=file_id, owner_type=owner_type, owner_id=owner_id
        )

    async def delete_file(self, file_id: int) -> None:
        """Delete file from storage and DB.

        Args:
            file_id: ID of the file to delete.

        Raises:
            ObjectNotFoundError: If file not found.
        """
        file = await super().get_one_object(object_id=file_id)
        await self.storage.delete(key=file.key)
        await super().delete_object(object_id=file_id)

    async def delete_all_by_owner(
        self, owner_type: OwnerType, owner_id: int
    ) -> None:
        """Delete all files for an owner.

        Args:
            owner_type: Type of owner (user/task/category).
            owner_id: ID of the owner.
        """
        files = await self.repository.get_by_owner(
            owner_type=owner_type, owner_id=owner_id
        )

        tasks = [
            self._delete_with_semaphore(file_id)
            for file_id in [f.id for f in files]
        ]

        await asyncio.gather(*tasks)

    async def _upload_with_semaphore(
        self,
        file: UploadFile,
        current_user: UserProfile,
        domain: str,
        owner_id: int,
    ) -> ResponseFileSchema:
        """Upload file with semaphore rate limiting.

        Args:
            file: File to upload.
            current_user: Current user.
            domain: Owner type.
            owner_id: Owner ID.

        Returns:
            File schema.
        """
        async with self._upload_semaphore:
            return await self.upload_file(
                file=file,
                current_user=current_user,
                domain=domain,
                owner_id=owner_id,
            )

    async def _delete_with_semaphore(self, file_id: int) -> None:
        """Delete file with semaphore rate limiting.

        Args:
            file_id: ID of file to delete.
        """
        async with self._delete_semaphore:
            file = await super().get_one_object(object_id=file_id)
            await self.storage.delete(key=file.key)
            await self.repository.delete_object(object_id=file_id)

    async def _upload_variant(
        self,
        suffix: str,
        data: bytes,
        domain: OwnerType,
        owner_id: int,
        file_name: str,
    ) -> tuple[str, int]:
        """Upload single image variant to storage.

        Args:
            suffix: Variant suffix (ORIGINAL/SMALL/THUMB).
            data: Image data bytes.
            domain: Owner type.
            owner_id: Owner ID.
            file_name: Original file name.

        Returns:
            Tuple of (storage_key, file_size_bytes).
        """
        key = self._get_key(
            domain=domain,
            owner_id=owner_id,
            file_name=f"{suffix}-{file_name}",
        )
        await self.storage.upload(
            key=key, file=BytesIO(data), real_mime="image/webp"
        )
        return key, len(data)

    async def _create_db_records(
        self,
        base_schema: ResponseFileSchema,
        current_user: UserProfile,
        upload_results: list[tuple[str, int]],
    ) -> list[ResponseFileSchema]:
        """Create DB records for uploaded variants.

        Args:
            base_schema: Base file schema template.
            current_user: User creating records.
            upload_results: List of (key, size) tuples.

        Returns:
            List of created file schemas.
        """
        records = []
        for key, size in upload_results:
            setattr(base_schema, "key", key)
            setattr(base_schema, "size", size)
            created = await super().create_object_with_author(
                object_data=base_schema, current_user=current_user
            )
            records.append(created)
        return records

    async def _verify_owner_exists(
        self, owner_type: str, owner_id: int
    ) -> None:
        """Verify owner exists in the system.

        Args:
            owner_type: Type of owner (user/task/category).
            owner_id: ID of the owner.

        Raises:
            ObjectNotFoundError: If owner not found.
        """
        owner_enum = OwnerType(owner_type)
        repo = self._get_owner_repository(owner_enum)

        owner_obj = await repo.get_object(owner_id)
        if owner_obj is None:
            raise ObjectNotFoundError(owner_id)

    def _get_owner_repository(
        self, owner_type: OwnerType
    ) -> TaskRepository | CategoryRepository | UserRepository:
        """Get appropriate repository for owner type.

        Args:
            owner_type: Type of owner.

        Returns:
            Repository instance for the owner type.
        """
        if owner_type == OwnerType.TASK:
            return TaskRepository(sessionmaker=self.repository.sessionmaker)
        if owner_type == OwnerType.CATEGORY:
            return CategoryRepository(
                sessionmaker=self.repository.sessionmaker
            )
        return UserRepository(sessionmaker=self.repository.sessionmaker)

    @staticmethod
    def _parse_owner_from_key(key: str) -> tuple[str, int]:
        """Parse owner type and ID from storage key.

        Key format: {owner_type}/{owner_id}/{uuid}-{filename}

        Args:
            key: Storage key string.

        Returns:
            Tuple of (owner_type, owner_id).
        """
        parts = key.split("/")
        return parts[0], int(parts[1])

    @staticmethod
    def _get_key(
        domain: OwnerType, owner_id: int, file_name: str
    ) -> str:
        """Generate storage key for file.

        Args:
            domain: Owner type.
            owner_id: Owner ID.
            file_name: Original file name.

        Returns:
            Formatted storage key.
        """
        return f"{domain}/{owner_id}/{uuid.uuid4()}-{file_name}"
