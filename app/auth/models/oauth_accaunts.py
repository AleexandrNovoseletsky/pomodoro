from datetime import date, datetime, timezone
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.database import Base


class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # 'yandex', 'google'...
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    birthday: Mapped[Optional[date]]
    email: Mapped[Optional[str]] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_profiles.id"), nullable=False
    )

    access_token: Mapped[Optional[str]] = mapped_column(String(1000))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("UserProfile", back_populates="oauth_accounts")

    __table_args__ = (
        UniqueConstraint(
            "provider", "provider_user_id", name="uq_provider_provider_user"
        ),
    )
