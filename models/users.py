import enum
from datetime import datetime, date, UTC
from typing import Optional

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from settings import Settings
from utils import make_check_in

settings = Settings()


class UserRole(enum.StrEnum):
    ROOT = "root"
    ADMIN = "admin"
    USER = "user"


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    phone: Mapped[Optional[str]] = mapped_column(
        String(12), nullable=False, unique=True
    )

    phone_verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    first_name: Mapped[str] = mapped_column(
        String(settings.MAX_USER_NAME_LENGTH), nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(settings.MAX_USER_NAME_LENGTH), nullable=False
    )
    patronymic: Mapped[Optional[str]] = mapped_column(
        String(settings.MAX_USER_NAME_LENGTH)
    )

    birthday: Mapped[Optional[date]]

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )

    email: Mapped[Optional[str]] = mapped_column(
        String(settings.MAX_EMAIL_LENGTH), unique=True
    )

    email_verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    photo_path: Mapped[Optional[str]] = mapped_column(String(255))

    about: Mapped[Optional[str]] = mapped_column(String(settings.MAX_USER_ABOUT_LENGTH))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role: Mapped[UserRole] = mapped_column(
        String(10), nullable=False, default=UserRole.USER.value
    )

    __table_args__ = (make_check_in(enum_cls=UserRole, column_name="role"),)
