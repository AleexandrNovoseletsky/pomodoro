"""Доступ к файлам хранилища minio."""

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from pomodoro.core.settings import Settings

settings = Settings()


class S3Storage:
    """Доступ к файлам."""
    def __init__(self):
        """Инициализируем доступ."""
        self.bucket = settings.S3_BUCKET

    async def _get_client(self):
        """Получаем клиента."""
        session = aioboto3.Session()
        return session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )

    async def upload(self, key: str, file: UploadFile, real_mime: str) -> None:
        """Загрузка файла в хранилище."""
        async with await self._get_client() as client:
            await client.upload_fileobj(
                file.file,
                Bucket=self.bucket,
                Key=key,
                ExtraArgs={"ContentType": real_mime}
                )

    async def delete(self, key: str) -> None:
        """Удаление файла."""
        async with await self._get_client() as client:
            await client.delete_object(
                Bucket=self.bucket,
                Key=key,
            )

    async def exists(self, key: str) -> bool:
        """Проверка наличия файла."""
        async with await self._get_client() as client:
            try:
                await client.head_object(Bucket=self.bucket, Key=key)
                return True
            except ClientError as exc:
                error_code = exc.response.get("Error", {}).get("Code")

                # S3 / MinIO коды "нет объекта"
                if error_code in ("404", "NoSuchKey", "NotFound"):
                    return False

                # Остальные ошибки — пробрасываем
                raise

    async def get_url(self, key: str) -> str:
        """Получение URL файла."""
        return f"{settings.S3_ENDPOINT}/{self.bucket}/{key}"

    async def generate_presigned_url(
            self, key: str, expires_in: int = 3600
            ) -> str:
        async with await self._get_client() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=expires_in
                )
