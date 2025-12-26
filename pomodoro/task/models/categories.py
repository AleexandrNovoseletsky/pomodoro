"""Category models.

Defines database models for category management with relationships to
tasks. Includes timestamp tracking and active status functionality.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pomodoro.core.mixins.active_flag import ActiveFlagMixin
from pomodoro.core.mixins.timestamp import TimestampMixin
from pomodoro.core.settings import Settings
from pomodoro.database.database import Base

settings = Settings()


class Category(TimestampMixin, ActiveFlagMixin, Base):
    """Category model for task categorization.

    Represents task categories with name uniqueness constraint and
    relationship to tasks. Includes automatic timestamp tracking and
    active/inactive status management.

    Attributes:
        id: Primary key identifier
        name: Unique category name with configurable maximum length
        tasks: Relationship to associated Task objects
               with cascade deletion
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(length=settings.MAX_CATEGORY_NAME_LENGTH),
        unique=True,
        nullable=False,
    )
    tasks = relationship(
        argument="Task",
        back_populates="category",
        cascade="all, delete-orphan",
    )
