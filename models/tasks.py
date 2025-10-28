from datetime import datetime, UTC

from sqlalchemy import Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.categories import Categories
from models.users import UserProfile
from settings import Settings

settings = Settings()


class Tasks(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name:  Mapped[str] = mapped_column(
        String(settings.MAX_TASK_NAME_LENGTH),
        unique=True, nullable=False
    )
    pomodoro_count: Mapped[int]

    category_id: Mapped[int] = mapped_column(
        ForeignKey(Categories.id),
        nullable=False
    )
    category = relationship(argument='Categories', backref='tasks')

    author_id: Mapped[int] = mapped_column(
        ForeignKey(UserProfile.id),
        nullable=False
    )

    author = relationship(argument='UserProfile', backref='tasks')

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), nullable=False
    )
