"""Mixins that add time flags to the model.

Provides reusable mixin classes for adding automatic timestamp tracking
to SQLAlchemy models. Enables creation and modification time tracking
for audit trails and temporal data management.
"""

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Adds automatic creation and modification timestamp tracking.

    Mixin class that provides created_at and updated_at datetime fields
    to SQLAlchemy models, enabling automatic tracking of record
    lifecycle for auditing, reporting, and temporal data analysis.

    Attributes:     created_at: UTC timestamp of when the record was
    initially created     updated_at: UTC timestamp of when the record
    was last modified,                automatically updated on each
    record modification

    Note:     Both timestamps use UTC timezone for consistency across
    timezones.     The updated_at field automatically refreshes on
    record updates     through SQLAlchemy's onupdate mechanism, ensuring
    accurate     modification tracking without manual intervention.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
        nullable=False,
        onupdate=datetime.now(UTC),
    )
