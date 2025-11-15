"""Модели медиа."""

import enum

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from pomodoro.core.mixins.timestamp import TimestampMixin
from pomodoro.core.utils.db_constraints import make_check_in
from pomodoro.database.database import Base


class OwnerType(enum.StrEnum):
    """К какой модели относится изображение."""

    USER = "user"
    TASK = "task"
    CATEGORY = "category"


class Variants(enum.StrEnum):
    """Варианты изображения."""

    ORIGINAL = "original"
    THUMB = "thumb"
    SMALL = "small"


class Files(TimestampMixin, Base):
    """Модель изображений."""

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    owner_type: Mapped[OwnerType] = mapped_column(
        String(50), nullable=False, index=True
        )
    author_id: Mapped[int] = mapped_column(nullable=False, index=True)
    bucket: Mapped[str] = mapped_column(String(256), nullable=False)
    key: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    variant: Mapped[Variants] = mapped_column(
        String(50), nullable=False, default=Variants.ORIGINAL.value
        )
    mime: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width: Mapped[int | None] = mapped_column(nullable=True)
    height: Mapped[int | None] = mapped_column(nullable=True)
    is_primary: Mapped[bool] = mapped_column(nullable=False, default=False)

    __table_args__ = (
        make_check_in(enum_cls=Variants, column_name="variant"),
        make_check_in(enum_cls=OwnerType, column_name="owner_type"),
        )
