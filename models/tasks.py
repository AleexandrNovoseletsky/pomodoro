from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models import Categories
from settings import Settings


settings = Settings()


class Tasks(Base):
    __tablename__ = 'Tasks'
    print(f"Model Base.metadata id: {id(Base.metadata)}")
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
