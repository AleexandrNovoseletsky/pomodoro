from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from settings import Settings


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
