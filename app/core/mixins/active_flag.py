"""Миксины добавляющие флаг is_active к модели."""

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column


class ActiveFlagMixin:
    """Добавляет флаг is_active к модели."""

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
