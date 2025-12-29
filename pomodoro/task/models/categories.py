"""Category models.

Defines database models for category management with relationships to
tasks.
Includes timestamp tracking and active status functionality.
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from pomodoro.core.mixins.active_flag import ActiveFlagMixin
from pomodoro.core.mixins.timestamp import TimestampMixin
from pomodoro.core.settings import Settings
from pomodoro.database.database import Base
from pomodoro.user.models.users import UserProfile

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
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey(column="categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    parent = relationship(
        argument="Category",
        remote_side=[id],
        back_populates="children",
    )
    children = relationship(
        argument="Category",
        back_populates="parent",
        cascade="all",
    )
    tasks = relationship(
        argument="Task",
        back_populates="category",
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey(UserProfile.id, ondelete="SET NULL"), nullable=True
    )
    author = relationship("UserProfile", back_populates="categories")
