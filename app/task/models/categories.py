"""Модели категорий."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins.active_flag import ActiveFlagMixin
from app.core.mixins.timestamp import TimestampMixin
from app.core.settings import Settings
from app.database.database import Base

settings = Settings()


class Category(TimestampMixin, ActiveFlagMixin, Base):
    """Модель категорий."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(settings.MAX_CATEGORY_NAME_LENGTH), unique=True, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    tasks = relationship(
        "Task",
        back_populates="category",
        cascade="all, delete-orphan",
    )
