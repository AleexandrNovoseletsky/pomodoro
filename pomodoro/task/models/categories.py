"""Модели категорий."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pomodoro.core.mixins.active_flag import ActiveFlagMixin
from pomodoro.core.mixins.timestamp import TimestampMixin
from pomodoro.core.settings import Settings
from pomodoro.database.database import Base

settings = Settings()


class Category(TimestampMixin, ActiveFlagMixin, Base):
    """Модель категорий."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(settings.MAX_CATEGORY_NAME_LENGTH), unique=True, nullable=False
    )
    tasks = relationship(
        "Task",
        back_populates="category",
        cascade="all, delete-orphan",
    )
