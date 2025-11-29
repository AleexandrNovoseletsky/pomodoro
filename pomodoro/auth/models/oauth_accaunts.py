"""Authorization models.

Defines database models for OAuth authentication and external identity
management. Includes models for storing OAuth provider accounts and
their relationships to users.
"""

from datetime import UTC, date, datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pomodoro.database.database import Base


class OAuthAccount(Base):
    """External OAuth accounts linked to user profiles.

    Stores OAuth provider data and access tokens for external
    authentication. Each user can have multiple OAuth accounts from
    different providers.

    Attributes:     id: Primary key identifier     provider: OAuth
    provider name (e.g., 'yandex', 'google')     provider_user_id:
    Unique user identifier from the OAuth provider     phone: Phone
    number from OAuth provider (optional)     first_name: First name
    from OAuth provider (optional)     last_name: Last name from OAuth
    provider (optional)     birthday: Birth date from OAuth provider
    (optional)     email: Email address from OAuth provider (optional)
    user_id: Foreign key to associated user profile     created_at:
    Timestamp of account creation     updated_at: Timestamp of last
    account update     user: Relationship to UserProfile model
    """

    __tablename__ = "oauth_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # OAuth provider identifiers: 'yandex', 'google', etc.
    provider: Mapped[str] = mapped_column(String(length=30), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(
        String(length=500), nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(length=255))
    first_name: Mapped[str | None] = mapped_column(String(length=255))
    last_name: Mapped[str | None] = mapped_column(String(length=255))
    birthday: Mapped[date | None]
    email: Mapped[str | None] = mapped_column(String(length=255))
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="user_profiles.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    user = relationship(
        argument="UserProfile", back_populates="oauth_accounts"
    )

    __table_args__ = (
        # Ensures unique provider-user_id combinations to prevent duplicates
        UniqueConstraint(
            "provider", "provider_user_id", name="uq_provider_provider_user"
        ),
        # Index for efficient user-based queries
        Index("ix_oauth_accounts_user_id", "user_id"),
        # Composite index for efficient provider-user lookups
        Index(
            "ix_oauth_accounts_provider_user", "provider", "provider_user_id"
        ),
    )
