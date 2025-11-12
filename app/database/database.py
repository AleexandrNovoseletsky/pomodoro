"""Классы для моделей БД."""

from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для моделей."""

    id: Any
    __allow_unmapped__ = True
