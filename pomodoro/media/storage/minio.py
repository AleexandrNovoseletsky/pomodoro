"""MinIO/S3 file storage access layer.

This module provides asynchronous file operations for MinIO/S3
compatible storage. Handles file uploads, deletions, existence checks,
and URL generation with proper error handling and resource management.
"""

from collections.abc import AsyncIterator
from typing import BinaryIO

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from pomodoro.core.settings import Settings

settings = Settings()


class S3Storage:
    """MinIO/S3 file storage client for asynchronous file operations.

    Provides a high-level interface for managing files in S3-compatible
    storage with proper connection pooling and error handling.

    Attributes:
        bucket: Target bucket name for all operations
    """

    def __init__(self) -> None:
        """Initialize S3 storage client with configured bucket."""
        self.bucket = settings.S3_BUCKET

    @staticmethod
    async def _get_client():
        """Create and return authenticated S3 client session.

        Returns:
            Async S3 client instance configured with
            application settings.

        Note:
            Uses aioboto3 session for proper
            async connection pooling.
            Client should be used within async context manager.
        """
        session = aioboto3.Session()
        return session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )

    async def upload(
            self,
            key: str,
            file: UploadFile | BinaryIO,
            mime: str,
    ) -> None:
        """Upload file to S3 storage.

        Args:
            key: Unique object key/path in bucket
            file: UploadFile or binary file-like object
            mime: MIME type for Content-Type header

        Raises:
            ValueError: If file type is not supported
        """
        async with await self._get_client() as client:
            if isinstance(file, UploadFile):
                fileobj = file.file
            elif hasattr(file, "read"):
                fileobj = file
                fileobj.seek(0)
            else:
                raise ValueError(
                    "Expected UploadFile or binary file-like object, "
                    f"got {type(file).__name__}"
                )

            await client.upload_fileobj(
                fileobj,
                Bucket=self.bucket,
                Key=key,
                ExtraArgs={"ContentType": mime},
            )

    async def delete(self, key: str) -> None:
        """Permanently delete file from storage.

        Warning! This operation is irreversible!

        Args:
            key: Object key to delete
        """
        async with await self._get_client() as client:
            await client.delete_object(
                Bucket=self.bucket,
                Key=key,
            )

    async def exists(self, key: str) -> bool:
        """Check if file exists in storage.

        Args:
            key: Object key to check

        Returns:
            True if file exists, False if not found

        Errors:
            ClientError: For S3 errors other than "not found"
        """
        async with await self._get_client() as client:
            try:
                await client.head_object(Bucket=self.bucket, Key=key)
                return True
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code")

                # Handle various "not found" error codes
                # across S3 implementations
                if error_code in ("404", "NoSuchKey", "NotFound"):
                    return False

                # Re-raise authentication, permission,
                # or other operational errors
                raise

    async def get_url(self, key: str) -> str:
        """Generate public URL for accessing file.

        Args:
            key: Object key to generate URL for

        Returns:
            Publicly accessible URL string
        """
        return f"{settings.S3_ENDPOINT}/{self.bucket}/{key}"

    async def generate_presigned_url(
        self, key: str, expires_in: int = 3600
    ) -> str:
        """Generate time-limited presigned URL.

        Args:
            key:
                Object key to generate URL for
            expires_in:
                URL validity duration in seconds
                (default: 1 hour)

        Returns:
            Presigned URL that provides temporary access to
            private files
        """
        async with await self._get_client() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in,
            )

    async def iter_keys(
        self,
        prefix: str | None = None,
    ) -> AsyncIterator[str]:
        """Iterate over all object keys in the bucket.

        Args:
            prefix: Optional key prefix to limit iteration

        Yields:
            Object keys stored in S3 bucket

        Notes:
            Uses list_objects_v2 with pagination.
            Safe for large buckets.
        """
        async with await self._get_client() as client:
            continuation_token: str | None = None

            while True:
                kwargs: dict[str, object] = {
                    "Bucket": self.bucket,
                    "MaxKeys": 1000,
                }

                if prefix:
                    kwargs["Prefix"] = prefix

                if continuation_token:
                    kwargs["ContinuationToken"] = continuation_token

                response = await client.list_objects_v2(**kwargs)

                for item in response.get("Contents", []):
                    yield item["Key"]

                if not response.get("IsTruncated"):
                    break

                continuation_token = response.get("NextContinuationToken")
