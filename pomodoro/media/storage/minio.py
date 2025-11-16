"""Async S3/MinIO storage operations."""

import io
from typing import Any

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from pomodoro.core.settings import Settings

settings = Settings()


class S3Storage:
    """Async S3-compatible object storage client.

    Supports MinIO and AWS S3 for file operations: upload, delete,
    existence checks, and presigned URL generation.
    """

    def __init__(self) -> None:
        """Initialize storage with configured bucket."""
        self.bucket = settings.S3_BUCKET
        self._session = aioboto3.Session()

    def _get_client_config(self) -> dict[str, Any]:
        """Get S3 client configuration.

        Returns:
            Configuration dictionary for S3 client initialization.
        """
        return {
            "endpoint_url": settings.S3_ENDPOINT,
            "aws_access_key_id": settings.S3_ACCESS_KEY,
            "aws_secret_access_key": settings.S3_SECRET_KEY,
        }

    async def upload(
        self, key: str, file: Any, real_mime: str
    ) -> None:
        """Upload file to S3 storage.

        Args:
            key: Object key in storage.
            file: File-like object (UploadFile, BytesIO, or bytes).
            real_mime: MIME type for the object.

        Raises:
            TypeError: If file type is not supported.
        """
        file_obj = self._prepare_file(file)

        async with self._session.client(
            "s3", **self._get_client_config()
        ) as client:
            await client.upload_fileobj(
                file_obj,
                Bucket=self.bucket,
                Key=key,
                ExtraArgs={"ContentType": real_mime},
            )

    async def delete(self, key: str) -> None:
        """Delete file from S3 storage.

        Args:
            key: Object key to delete.
        """
        async with self._session.client(
            "s3", **self._get_client_config()
        ) as client:
            await client.delete_object(Bucket=self.bucket, Key=key)

    async def exists(self, key: str) -> bool:
        """Check if object exists in storage.

        Args:
            key: Object key to check.

        Returns:
            True if object exists, False otherwise.

        Raises:
            ClientError: For non-404 S3 errors.
        """
        async with self._session.client(
            "s3", **self._get_client_config()
        ) as client:
            try:
                await client.head_object(Bucket=self.bucket, Key=key)
                return True
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code")
                if error_code in ("404", "NoSuchKey", "NotFound"):
                    return False
                raise

    async def get_url(self, key: str) -> str:
        """Get public URL for object.

        Args:
            key: Object key.

        Returns:
            Public URL string.
        """
        return f"{settings.S3_ENDPOINT}/{self.bucket}/{key}"

    async def generate_presigned_url(
        self, key: str, expires_in: int = 3600
    ) -> str:
        """Generate temporary presigned URL for object.

        Args:
            key: Object key.
            expires_in: URL expiration time in seconds (default 3600).

        Returns:
            Presigned URL string.
        """
        async with self._session.client(
            "s3", **self._get_client_config()
        ) as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )

    @staticmethod
    def _prepare_file(file: Any) -> Any:
        """Prepare file object for upload.

        Args:
            file: UploadFile, BytesIO, bytes, or file-like object.

        Returns:
            File-like object with read() method.

        Raises:
            TypeError: If file type is not supported.
        """
        if isinstance(file, UploadFile):
            return file.file
        if isinstance(file, bytes):
            return io.BytesIO(file)
        if hasattr(file, "read"):
            return file
        raise TypeError(
            "Unsupported file type. Expected UploadFile, BytesIO, "
            "bytes, or file-like object."
        )
