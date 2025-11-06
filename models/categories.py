from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from mixins import ActiveFlagMixin
from mixins import TimestampMixin
from settings import Settings

settings = Settings()


class Categories(TimestampMixin, ActiveFlagMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(settings.MAX_CATEGORY_NAME_LENGTH), unique=True, nullable=False
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
