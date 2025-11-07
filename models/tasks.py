from sqlalchemy import String, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from mixins import ActiveFlagMixin
from mixins import TimestampMixin
from models.categories import Category
from models.users import UserProfile
from settings import Settings

settings = Settings()


class Task(ActiveFlagMixin, TimestampMixin, Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(settings.MAX_TASK_NAME_LENGTH), unique=True, nullable=False
    )
    pomodoro_count: Mapped[int] = mapped_column(SmallInteger())

    category_id: Mapped[int] = mapped_column(
        ForeignKey(Category.id), nullable=False
    )
    category = relationship(argument="Category", backref="tasks")

    author_id: Mapped[int] = mapped_column(
        ForeignKey(UserProfile.id), nullable=False
    )

    author = relationship(argument="UserProfile", backref="tasks")
