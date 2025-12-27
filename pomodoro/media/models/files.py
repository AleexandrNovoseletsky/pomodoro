"""Media models."""

import enum

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from pomodoro.core.mixins.timestamp import TimestampMixin
from pomodoro.core.utils.db_constraints import make_check_in
from pomodoro.database.database import Base
from pomodoro.media.owners.registry import OwnerType
from pomodoro.user.models.users import UserProfile


class AllowedMimeTypes(enum.StrEnum):
    """Allowed file types."""

    JPEG = "image/jpeg"
    PNG = "image/png"
    WEBP = "image/webp"
    PDF = "application/pdf"
    TEXT_PLAIN = "text/plain"
    TEXT_RTF = "text/rtf"


class Variants(enum.StrEnum):
    """Image Options."""

    ORIGINAL = "original"
    THUMB = "thumb"
    SMALL = "small"


class Files(TimestampMixin, Base):
    """The file model."""

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # What entity is the file attached to: user / task / category
    owner_type: Mapped[OwnerType] = mapped_column(
        String(50), nullable=False, index=True
    )

    # Entity ID (task.id, user.id, category.id)
    owner_id: Mapped[int] = mapped_column(nullable=False, index=True)

    # The author of the file upload
    author_id: Mapped[int] = mapped_column(
        ForeignKey(UserProfile.id, ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    bucket: Mapped[str] = mapped_column(String(256), nullable=False)
    key: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)

    variant: Mapped[Variants] = mapped_column(
        String(50), nullable=False, default=Variants.ORIGINAL.value
    )

    mime: Mapped[AllowedMimeTypes] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)

    width: Mapped[int | None] = mapped_column(nullable=True)
    height: Mapped[int | None] = mapped_column(nullable=True)

    is_primary: Mapped[bool] = mapped_column(nullable=False, default=False)

    __table_args__ = (
        make_check_in(enum_cls=AllowedMimeTypes, column_name="mime"),
        make_check_in(enum_cls=Variants, column_name="variant"),
        make_check_in(enum_cls=OwnerType, column_name="owner_type"),
    )
