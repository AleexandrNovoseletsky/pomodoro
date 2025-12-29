"""File validation and image processing utilities."""

import asyncio
import io
import logging

import magic
from fastapi import UploadFile
from PIL import Image
from pydantic import ValidationError

from pomodoro.core.exceptions.file import (
    InvalidCreateFileData,
)
from pomodoro.core.settings import Settings
from pomodoro.media.models.files import OwnerType
from pomodoro.media.schemas.media import CreateFileSchema

settings = Settings()

logger = logging.getLogger(__name__)


class FileChecker:
    """Validates and processes uploaded files.

    Handles file type validation via magic bytes, image dimension
    checks, aspect ratio validation, and WebP conversion for multiple
    variants.
    """

    MIME_HEADER_SIZE = 2048
    # Slightly reduced quality to speed up WebP encoding without visible loss
    WEBP_QUALITY = 80
    IMAGE_FORMAT = "WEBP"

    def __init__(self, file: UploadFile) -> None:
        """Initialize file processor.

        Args:
        file: Uploaded file from FastAPI.
        """
        self.file = file
        self._file_bytes: bytes | None = None

    async def validate_file(
        self,
        domain: OwnerType,
        owner_id: int,
        author_id: int,
        key: str,
    ) -> CreateFileSchema:
        """Validate and create file schema.

        Args:     domain: Owner type (user/task/category).     owner_id:
        ID of the owner.     author_id: ID of the user uploading.
        key: Storage key for the file.

        Returns:     Validated CreateFileSchema instance.

        Errors:     InvalidCreateFileData: If validation fails.
        """
        try:
            mime = await self._get_real_mime()
            file_data = CreateFileSchema(
                owner_type=domain,
                owner_id=owner_id,
                author_id=author_id,
                mime=mime,
                size=self.file.size,
                key=key,
            )
        except ValidationError as exc:
            raise InvalidCreateFileData(
                exc=exc,
                detail=(
                    f"File '{self.file.filename}': "
                    f"{InvalidCreateFileData.format_errors(exc)}"
                ),
            ) from exc
        return file_data

    async def process_image(self) -> dict[str, bytes]:
        """Async wrapper that image processing to a thread.

        Pillow is CPU-bound and blocks the event loop; running the work
        in a thread prevents blocking other async tasks. This method
        reads the bytes asynchronously then delegates the heavy work to
        :meth:`_process_image_sync` via :func:`asyncio.to_thread`.
        """
        file_bytes = await self._read_file_bytes()

        # Validate MIME quickly in the event loop (cheap) before offloading.
        mime = magic.from_buffer(file_bytes, mime=True)
        if not mime.startswith("image/"):
            raise InvalidCreateFileData(
                exc=None,
                detail=(
                    f"File '{self.file.filename}' "
                    f"is not an image (mime={mime})"
                ),
            )

        # Offload synchronous Pillow processing to a thread to avoid blocking.
        return await asyncio.to_thread(self._process_image_sync, file_bytes)

    async def check_file(
        self,
        domain: OwnerType,
        owner_id: int,
        author_id: int,
        key: str,
    ) -> CreateFileSchema:
        """Alias for validate_file for backward compatibility.

        Args:     domain: Owner type.     owner_id: ID of the owner.
        author_id: ID of the uploader.     key: Storage key.

        Returns:     Validated CreateFileSchema instance.
        """
        return await self.validate_file(domain, owner_id, author_id, key)

    async def _read_file_bytes(self) -> bytes:
        """Read file content and reset position.

        Returns:     File content as bytes.
        """
        if self._file_bytes is None:
            self._file_bytes = await self.file.read()
            await self.file.seek(0)
        return self._file_bytes

    async def _get_real_mime(self) -> str:
        """Detect actual MIME type via magic bytes.

        Returns:     MIME type string.
        """
        header = await self.file.read(self.MIME_HEADER_SIZE)
        mime = magic.from_buffer(header, mime=True)
        await self.file.seek(0)
        return mime

    @staticmethod
    def _validate_image_dimensions(img: Image.Image) -> None:
        """Validate image minimum dimensions.

        Args:     img: PIL Image object.

        Errors:     InvalidCreateFileData: If dimensions are below
        minimum.
        """
        width, height = img.size
        min_w, min_h = settings.MIN_IMAGE_SIZE

        if width < min_w or height < min_h:
            raise InvalidCreateFileData(
                exc=None,
                detail=(
                           f"Minimum resolution {min_w}x{min_h}, "
                            f"received {width}x{height}"
                ),
            )

    @staticmethod
    def _validate_aspect_ratio(img: Image.Image) -> None:
        """Validate image aspect ratio.

        Args:     img: PIL Image object.

        Errors:     InvalidCreateFileData: If aspect ratio doesn't
        match.
        """
        width, height = img.size
        ratio = settings.RATIO

        actual_ratio = round(width / height, 4)
        expected_ratio = round(ratio[0] / ratio[1], 4)

        if actual_ratio != expected_ratio:
            raise InvalidCreateFileData(
                exc=None,
                detail=(
                    f"Expected ratio {ratio[0]}:{ratio[1]}, "
                    f"received {width}:{height}"
                ),
            )

    def _generate_variants(self, img: Image.Image) -> dict[str, bytes]:
        """Generate image variants (original, small, thumbnail).

        Args:     img: PIL Image object.

        Returns:     Dictionary with variant names as keys and WebP
        bytes as values.
        """
        # Generate each variant and log per-variant timings inside
        original = self._convert_to_webp(img)

        small_img = img.copy()
        small_img = small_img.resize(
            settings.SMALL_SIZE,
            Image.Resampling.LANCZOS,
        )
        small = self._convert_to_webp(small_img)

        thumb_img = img.copy()
        thumb_img = thumb_img.resize(
            settings.THUMB_SIZE,
            Image.Resampling.LANCZOS,
        )
        thumb = self._convert_to_webp(thumb_img)

        return {
            "original": original,
            "small": small,
            "thumb": thumb,
        }

    def _convert_to_webp(self, img: Image.Image) -> bytes:
        """Convert PIL Image to WebP format and log duration.

        This is a synchronous CPU bound operation and is executed in a
        thread via :func:`asyncio.to_thread` from the async wrapper.
        """
        out = io.BytesIO()
        img.save(
            out,
            format=self.IMAGE_FORMAT,
            quality=self.WEBP_QUALITY,
            method=0,
            lossless=False,
        )
        return out.getvalue()

    def _process_image_sync(self, file_bytes: bytes) -> dict[str, bytes]:
        """Synchronous image processing using Pillow.

        This method is intended to be executed in a separate thread via
        :func:`asyncio.to_thread` to keep the async event loop
        responsive. Adds detailed timing logs for each internal step.
        """
        with Image.open(io.BytesIO(file_bytes)) as img:
            self._validate_image_dimensions(img)
            self._validate_aspect_ratio(img)
            variants = self._generate_variants(img)

        return variants
