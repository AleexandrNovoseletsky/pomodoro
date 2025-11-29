"""Classes for database models."""

from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for models."""

    id: Any
    __allow_unmapped__ = True
