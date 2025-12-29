"""Task models.

Defines database models for task management with relationships to
categories and users. Includes pomodoro tracking, timestamp management,
and active status functionality.
"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pomodoro.core.mixins.active_flag import ActiveFlagMixin
from pomodoro.core.mixins.timestamp import TimestampMixin
from pomodoro.core.settings import Settings
from pomodoro.database.database import Base
from pomodoro.task.models.categories import Category
from pomodoro.task.models.task_tags import task_tag_table
from pomodoro.user.models.users import UserProfile

if TYPE_CHECKING:
    from pomodoro.task.models.tags import Tag

settings = Settings()


class Task(ActiveFlagMixin, TimestampMixin, Base):
    """Task model for pomodoro task management.

    Represents individual tasks with pomodoro tracking, categorization,
    and user ownership. Includes automatic timestamp tracking and
    active/inactive status management.

    Attributes:
        id: Primary key identifier
        name: Unique task name with configurable maximum length
        pomodoro_count: Number of pomodoro intervals
                        allocated for the task
        category_id: Foreign key to associated
                     category with CASCADE delete
        category: Relationship to Category model
        author_id: Foreign key to task creator with CASCADE delete
        author: Relationship to UserProfile model
    """

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
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=task_tag_table,
        back_populates="tasks",
        lazy="selectin",
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey(UserProfile.id, ondelete="SET NULL"), nullable=True
    )
    author = relationship("UserProfile", back_populates="tasks")
