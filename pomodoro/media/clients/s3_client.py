"""S3 Object Storage Client."""

import aioboto3
from botocore.config import Config

from pomodoro.core.settings import Settings

settings = Settings()


async def get_s3_client() -> aioboto3.Session:
    """Creating an S3 Client."""
    session = aioboto3.Session()

    return session.client(
        service_name="s3",
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        endpoint_url=settings.S3_ENDPOINT,
    )
