"""Модели пользователей."""

import enum
from datetime import date

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.auth.models.oauth_accaunts import OAuthAccount  # noqa: F401
from app.core.mixins.active_flag import ActiveFlagMixin
from app.core.mixins.timestamp import TimestampMixin
from app.core.settings import Settings
from app.core.utils.db_constraints import make_check_in
from app.database.database import Base

settings = Settings()


class UserRole(enum.StrEnum):
    """Роли пользователей."""

    ROOT = "root"
    ADMIN = "admin"
    USER = "user"


class UserProfile(ActiveFlagMixin, TimestampMixin, Base):
    """Модель пользователя."""

    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    phone: Mapped[str | None] = mapped_column(String(12), unique=True)

    phone_verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    first_name: Mapped[str | None] = mapped_column(
        String(settings.MAX_USER_NAME_LENGTH)
    )
    last_name: Mapped[str | None] = mapped_column(
        String(settings.MAX_USER_NAME_LENGTH)
    )
    patronymic: Mapped[str | None] = mapped_column(
        String(settings.MAX_USER_NAME_LENGTH)
    )

    birthday: Mapped[date | None]

    email: Mapped[str | None] = mapped_column(
        String(settings.MAX_EMAIL_LENGTH), unique=True
    )

    email_verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    hashed_password: Mapped[str | None] = mapped_column(String(255))

    photo_path: Mapped[str | None] = mapped_column(String(255))

    about: Mapped[str | None] = mapped_column(
        String(settings.MAX_USER_ABOUT_LENGTH)
    )

    role: Mapped[UserRole] = mapped_column(
        String(10), nullable=False, default=UserRole.USER.value
    )
    tasks = relationship(
        "Task",
        back_populates="author",
        cascade="all, delete-orphan",
    )
    oauth_accounts = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    __table_args__ = (make_check_in(enum_cls=UserRole, column_name="role"),)
