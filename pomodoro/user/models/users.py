"""User models.

Defines database models for user management including profiles, roles,
and relationships. Includes user authentication fields, profile
information, and relationships to tasks and OAuth accounts.
"""

import enum
from datetime import date

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pomodoro.auth.models.oauth_accaunts import OAuthAccount  # noqa: F401
from pomodoro.core.mixins.active_flag import ActiveFlagMixin
from pomodoro.core.mixins.timestamp import TimestampMixin
from pomodoro.core.settings import Settings
from pomodoro.core.utils.db_constraints import make_check_in
from pomodoro.database.database import Base

settings = Settings()


class UserRole(enum.StrEnum):
    """User role enumeration for access control.

    Defines hierarchical user roles for permission management: - ROOT:
    System administrator with full access - ADMIN: Administrative user
    with elevated privileges - USER: Regular application user with
    standard access
    """

    ROOT = "root"
    ADMIN = "admin"
    USER = "user"


class UserProfile(ActiveFlagMixin, TimestampMixin, Base):
    """User profile model for user management and authentication.

    Represents user entities with comprehensive profile information,
    authentication credentials, and relationships to other system
    entities. Includes timestamp tracking and active status management.

    Attributes:     id: Primary key identifier     phone: Unique phone
    number for authentication     phone_verified: Phone number
    verification status     first_name: User's first name     last_name:
    User's last name     patronymic: User's patronymic/middle name
    birthday: User's date of birth     email: Unique email address
    email_verified: Email verification status     hashed_password:
    Securely stored password hash     about: User biography or
    description     role: User role for access control     tasks:
    Relationship to user's tasks with cascade deletion
    oauth_accounts: Relationship to OAuth accounts with cascade deletion
    """

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
    about: Mapped[str | None] = mapped_column(
        String(settings.MAX_USER_ABOUT_LENGTH)
    )
    role: Mapped[UserRole] = mapped_column(
        String(50), nullable=False, default=UserRole.USER.value
    )
    categories = relationship(
        argument="Category",
        back_populates="author",
    )
    tasks = relationship(
        argument="Task",
        back_populates="author",
    )
    tags = relationship(
        argument="Tag",
        back_populates="author",
    )
    oauth_accounts = relationship(
        argument="OAuthAccount",
        back_populates="user",
    )

    __table_args__ = (make_check_in(enum_cls=UserRole, column_name="role"),)
