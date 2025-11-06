from datetime import datetime, UTC
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, func


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
        nullable=False
    )
