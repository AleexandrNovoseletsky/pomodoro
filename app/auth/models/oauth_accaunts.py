"""Модели авторизации."""

from datetime import UTC, date, datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class OAuthAccount(Base):
    """Модель внешнего пользователя от провайдера авторизации."""

    __tablename__ = "oauth_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 'yandex', 'google'...
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    birthday: Mapped[date | None]
    email: Mapped[str | None] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id"), nullable=False
    )

    access_token: Mapped[str | None] = mapped_column(String(1000))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    user = relationship("UserProfile", back_populates="oauth_accounts")

    __table_args__ = (
        UniqueConstraint(
            "provider", "provider_user_id", name="uq_provider_provider_user"
        ),
    )
