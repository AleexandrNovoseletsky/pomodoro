from typing import Optional

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


Base = declarative_base()

class Categories(Base):
    __tablename__ = 'Categories'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(10), unique=True, nullable=False
    )

class Tasks(Base):
    __tablename__ = 'Tasks'

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    name:  Mapped[str] = mapped_column(
        String(25), unique=True, nullable=False
    )
    pomodoro_count: Mapped[int]
    category_id: Mapped[int] = mapped_column(ForeignKey(Categories.id))
