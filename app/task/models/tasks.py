"""Модели задач."""

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.mixins.active_flag import ActiveFlagMixin
from app.core.mixins.timestamp import TimestampMixin
from app.core.settings import Settings
from app.database.database import Base
from app.task.models.categories import Category
from app.user.models.users import UserProfile

settings = Settings()


class Task(ActiveFlagMixin, TimestampMixin, Base):
    """Модель задач."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(settings.MAX_TASK_NAME_LENGTH), unique=True, nullable=False
    )
    pomodoro_count: Mapped[int] = mapped_column(SmallInteger())

    category_id: Mapped[int] = mapped_column(
        ForeignKey(Category.id, ondelete="CASCADE"), nullable=False
    )
    category = relationship("Category", back_populates="tasks")

    author_id: Mapped[int] = mapped_column(
        ForeignKey(UserProfile.id, ondelete="CASCADE"), nullable=False
    )

    author = relationship("UserProfile", back_populates="tasks")
