"""Схемы медиа."""

from datetime import datetime

from pydantic import BaseModel, Field

from pomodoro.core.settings import Settings
from pomodoro.media.models.files import AllowedMimeTypes, OwnerType, Variants

settings = Settings()


class CreateFileSchema(BaseModel):
    """Принимаемые данные для создания файла."""

    owner_type: OwnerType
    owner_id: int
    author_id: int
    mime: AllowedMimeTypes
    key: str
    size: int = Field(..., le=settings.MAX_FILE_SIZE)
    bucket: str | None = settings.S3_BUCKET
    variant: Variants | None = None


class ResponseFileSchema(CreateFileSchema):
    """Возвращаеые пользователю данные."""
    id: int
    key: str
    variant: Variants | None = None
    width: int | None = None
    height: int | None = None
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SetPrimarySchema(BaseModel):
    """Сделать изображение главным."""
    is_primary: bool
