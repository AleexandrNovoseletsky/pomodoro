"""Схемы медиа."""

from datetime import datetime

from pydantic import BaseModel, Field

from pomodoro.core.settings import Settings
from pomodoro.media.models.files import OwnerType, Variants

settings = Settings()


class CreateFileSchema(BaseModel):
    """Принимаемые данные для создания файла."""

    owner_type: OwnerType
    owner_id: int
    author_id: int
    mime: str
    key: str
    size: int = Field(..., le=settings.MAX_FILE_SIZE)
    bucket: str | None = settings.S3_BUCKET


class ResponseFileSchema(CreateFileSchema):
    id: int
    key: str
    variant: Variants | None = None
    width: int | None = None
    height: int | None = None
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
