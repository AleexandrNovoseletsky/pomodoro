"""Tags models.

Defines database models for tags management with relationships to
tasks and categories.
Includes timestamp tracking and active status functionality.
"""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pomodoro.core.mixins.active_flag import ActiveFlagMixin
from pomodoro.core.mixins.timestamp import TimestampMixin
from pomodoro.core.settings import Settings
from pomodoro.database.database import Base
from pomodoro.task.models.task_tags import task_tag_table
from pomodoro.user.models.users import UserProfile

if TYPE_CHECKING:
    from pomodoro.task.models.tasks import Task

settings = Settings()


class Tag(ActiveFlagMixin, TimestampMixin, Base):
    """Task tag.

    Represents a label that can be assigned to tasks for classification
    and filtering purposes.
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(length=settings.MAX_TASK_NAME_LENGTH),
        unique=True,
        nullable=False,
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary=task_tag_table,
        back_populates="tags",
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey(UserProfile.id, ondelete="SET NULL"), nullable=True
    )
    author = relationship("UserProfile", back_populates="tags")
