"""Media services.

This module provides media file management services including upload,
processing, storage, and retrieval of files with support for multiple
variants and formats. Handles image processing, file validation, and
integration with S3-compatible storage.
"""

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
from pomodoro.media.converters.image_converters import (
    convert_to_webp,
    resize_image,
)
from pomodoro.media.models.files import (
    AllowedMimeTypes,
    Files,
    OwnerType,
    Variants,
)
from pomodoro.media.repositories.media import MediaRepository
from pomodoro.media.schemas.media import CreateFileSchema, ResponseFileSchema
from pomodoro.media.storage.minio import S3Storage
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.user.models.users import UserProfile
from pomodoro.user.repositories.user import UserRepository

settings = Settings()


class MediaService(CRUDService[ResponseFileSchema]):
    """Media file management service.

    Provides comprehensive file operations including upload, processing,
    storage, and retrieval with support for multiple file variants and
    formats.
    """

    repository = MediaRepository

    def __init__(self, media_repo: MediaRepository):
        """Initialize media service with repository and storage.

        Args:     media_repo: Media repository instance for database
        operations
        """
        self.storage = S3Storage()
        self.repository = media_repo
        super().__init__(
            repository=media_repo, response_schema=ResponseFileSchema
        )

    async def get_presigned_url(self, file_id: int) -> str:
        """Generate presigned URL for temporary file access.

        Args:     file_id: The identifier of the file to generate URL
        for

        Returns:     Temporary presigned URL with limited access
        duration

        Raises:     ObjectNotFoundError: If file with given ID doesn't
        exist
        """
        file = await super().get_one_object(object_id=file_id)
        return await self.storage.generate_presigned_url(key=file.key)

    async def get_by_owner(
        self, domain: OwnerType, owner_id: int
    ) -> list[ResponseFileSchema]:
        """Retrieve all files belonging to a specific resource.

        Args:     domain: The domain type to which files belong (Task,
        User, Category)     owner_id: The resource ID to which files
        belong

        Returns:     List of validated file response schemas

        Note:     Returns empty list if no files found for the owner
        """
        files = await self.repository.get_by_owner(
            domain=domain, owner_id=owner_id
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
        """Upload file to storage and save metadata to database.

        Performs file validation, MIME type detection, owner
        verification, and storage upload in a single transaction.

        Args:
            file: Uploaded file object
            current_user: User who initiated the upload
            domain: Domain type the file belongs to (Task, User, Category)
            owner_id: Resource ID the file belongs to

        Returns:
        Validated file response schema with upload details

        Raises:
        InvalidCreateFileData: If file validation fails
        ObjectNotFoundError: If owner resource doesn't exist
        ValueError: If MIME type is not allowed
        """
        key: str = f"{domain}/{owner_id}/{uuid.uuid4()}-{file.filename}"
        mime: AllowedMimeTypes = await self._get_real_mime(file=file)
        try:
            # Validate file data and create schema
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

        # Verify owner resource exists before upload
        await self._verify_owner_exists(owner_type=domain, owner_id=owner_id)

        # Upload file to S3 storage
        await self.storage.upload(key=key, file=file, mime=mime)

        # Save file metadata to database
        return await super().create_object(object_data=file_data)

    async def upload_image(
        self,
        image: UploadFile,
        current_user: UserProfile,
        domain: OwnerType,
        owner_id: int,
    ) -> list[ResponseFileSchema]:
        """Upload image and create multiple variants.

        Generates three image variants: - ORIGINAL: Full resolution WebP
        format - SMALL: Medium resolution for general display - THUMB:
        Highly compressed for thumbnails and previews

        Args:     image: Uploaded image file     current_user: User who
        initiated the upload     domain: Domain type the image belongs
        to     owner_id: Resource ID the image belongs to

        Returns:     List of three file response schemas [ORIGINAL,
        SMALL, THUMB]

        Raises:     ObjectNotFoundError: If owner resource doesn't exist
        Exception: Rolls back all uploads if database operation fails
        """
        # Extract filename without extension for variant naming
        filename = Path(image.filename).stem

        # Verify owner resource exists before processing
        await self._verify_owner_exists(owner_type=domain, owner_id=owner_id)

        # Generate unique keys for each variant
        keys: list[str] = await self._get_variant_keys(
            domain=domain, owner_id=owner_id, filename=filename
        )

        # Process image and create variants
        original_image_bytes: bytes = await image.read()
        files: list[io.BytesIO] = []
        files.append(await convert_to_webp(image=original_image_bytes))
        files.append(
            await resize_image(image=files[0], width=settings.SMALL_WIDTH)
        )
        files.append(
            await resize_image(image=files[1], width=settings.THUMB_WIDTH)
        )

        # Upload all variants to storage
        upload_data: dict[str, io.BytesIO] = dict(
            zip(keys, files, strict=True)
        )
        mime = AllowedMimeTypes.WEBP
        await self._upload_variants(files=upload_data, mime=mime)

        # Save file metadata to database with rollback protection
        try:
            # Generate file schemas for each variant
            author_id = current_user.id
            schemas_data = {
                "owner_type": domain,
                "owner_id": owner_id,
                "author_id": author_id,
                "mime": mime,
            }
            schemas: list[CreateFileSchema] = [
                CreateFileSchema(
                    **schemas_data,
                    size=sys.getsizeof(files[0]),
                    key=keys[0],
                    variant=Variants.ORIGINAL,
                ),
                CreateFileSchema(
                    **schemas_data,
                    size=sys.getsizeof(files[1]),
                    key=keys[1],
                    variant=Variants.SMALL,
                ),
                CreateFileSchema(
                    **schemas_data,
                    size=sys.getsizeof(files[2]),
                    key=keys[2],
                    variant=Variants.THUMB,
                ),
            ]

            # Create database records for all variants
            db_files = [
                await super().create_object(object_data=schemas[0]),
                await super().create_object(object_data=schemas[1]),
                await super().create_object(object_data=schemas[2]),
            ]
            return db_files

        # Rollback storage upload if database operation fails
        except Exception:
            for key in keys:
                await self.storage.delete(key=key)
            raise

    async def set_primary(self, file_id: int) -> ResponseFileSchema:
        """Set a file as primary for its owner resource.

        Marks the specified file as the primary/default file for the
        owner resource, demoting any previously set primary file.

        Args:     file_id: The file ID to set as primary

        Returns:     Updated file response schema with primary status

        Raises:     ObjectNotFoundError: If file doesn't exist
        """
        file: ResponseFileSchema = await super().get_one_object(
            object_id=file_id
        )
        file_key = file.key
        owner_type, owner_id = await self._get_owner_and_owner_id_by_key(
            key=file_key
        )
        file: Files = await self.repository.set_primary(
            file_id=file_id, domain=owner_type, owner_id=owner_id
        )
        return ResponseFileSchema.model_validate(file)

    async def delete_file(self, file_id: int) -> None:
        """Delete file from both storage and database.

        Performs complete file removal including: - Physical file
        deletion from S3 storage - Metadata removal from database

        Args:     file_id: ID of the file to delete

        Raises:     ObjectNotFoundError: If file doesn't exist
        """
        # Retrieve file metadata from database
        file = await super().get_one_object(object_id=file_id)

        # Delete physical file from storage
        await self.storage.delete(key=file.key)

        # Remove file metadata from database
        return await super().delete_object(object_id=file_id)

    async def delete_all_by_owner(
        self, domain: OwnerType, owner_id: int
    ) -> None:
        """Delete all files belonging to a specific resource.

        Performs bulk deletion of all files associated with an owner
        using concurrent operations for efficiency.

        Args:     domain: Domain type to delete files for     owner_id:
        Resource ID to delete files for

        Note:     Uses semaphore to limit concurrent storage operations
        to prevent resource exhaustion
        """
        files = await self.repository.get_by_owner(
            domain=domain, owner_id=owner_id
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
        """Verify that owner resource exists in the system.

        Checks the appropriate repository based on owner type to ensure
        the referenced resource exists before file operations.

        Args:     owner_type: Type of owner resource (Task, Category,
        User)     owner_id: ID of owner resource to verify

        Raises:     ObjectNotFoundError: If owner resource doesn't exist
        """
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
        self, files: dict[str, io.BytesIO], mime: AllowedMimeTypes
    ) -> None:
        """Upload multiple file variants to storage.

        Args:     files: Dictionary mapping storage keys to file buffers
        mime: MIME type for all uploaded variants
        """
        for key, file in files.items():
            await self.storage.upload(key=key, file=file, mime=mime)

    @staticmethod
    async def _get_owner_and_owner_id_by_key(key: str) -> tuple[str, int]:
        """Extract owner type and ID from storage key.

        Args:     key: Storage key in format "domain/owner_id/filename"

        Returns:     Tuple of (owner_type, owner_id)
        """
        split_key = key.split(sep="/")
        return split_key[0], int(split_key[1])

    @staticmethod
    async def _get_real_mime(file: UploadFile) -> AllowedMimeTypes:
        """Detect actual MIME type using file content.

        Reads file header to determine real MIME type rather than
        relying on client-provided content type.

        Args:
            file: Uploaded file to analyze

        Returns:
            Validated allowed MIME type

        Raises:
            ValueError: If detected MIME type is not in allowed list
        """
        header = await file.read(2048)
        real_mime = magic.from_buffer(header, mime=True)
        await file.seek(0)
        try:
            return AllowedMimeTypes(real_mime)
        except ValueError as err:
            raise ValueError(f"Invalid file type {real_mime}.") from err

    @staticmethod
    async def _get_key(
        domain: OwnerType,
        owner_id: int,
        filename: str,
    ) -> str:
        """Generate storage key for file.

        Args:     domain: Owner domain type     owner_id: Owner resource
        ID     filename: Original filename

        Returns:     Unique storage key with UUID for collision
        avoidance
        """
        return f"{domain}/{owner_id}/{uuid.uuid4()}-{filename}.webp"

    @staticmethod
    async def _get_variant_keys(
        domain: OwnerType,
        owner_id: int,
        filename: str,
    ) -> list[str]:
        """Generate storage keys for all image variants.

        Args:     domain: Owner domain type     owner_id: Owner resource
        ID     filename: Original filename

        Returns:     List of three unique storage keys for [ORIGINAL,
        SMALL, THUMB]
        """
        return [
            f"{domain}/{owner_id}/{uuid.uuid4()}-{Variants.ORIGINAL}-{filename}.webp",
            f"{domain}/{owner_id}/{uuid.uuid4()}-{Variants.SMALL}-{filename}.webp",
            f"{domain}/{owner_id}/{uuid.uuid4()}-{Variants.THUMB}-{filename}.webp",
        ]
