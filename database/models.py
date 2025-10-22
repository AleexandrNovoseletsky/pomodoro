from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from settings import Settings


Base = declarative_base()
settings = Settings()

class Categories(Base):
    __tablename__ = 'Categories'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(settings.MAX_CATEGORY_NAME_LENGTH),
        unique=True,
        nullable=False
    )

class Tasks(Base):
    __tablename__ = 'Tasks'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name:  Mapped[str] = mapped_column(
        String(settings.MAX_TASK_NAME_LENGTH),
        unique=True,
        nullable=False
    )
    pomodoro_count: Mapped[int]
    category_id: Mapped[int] = mapped_column(ForeignKey(Categories.id))
