"""Mixins that add the is_active flag to the model.

Provides reusable mixin classes for adding soft deletion capabilities to
SQLAlchemy models through an is_active flag. Enables record deactivation
instead of physical deletion for data preservation.
"""

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column


class ActiveFlagMixin:
    """Adds soft deletion capability through an is_active flag.

    Mixin class that provides an is_active boolean field to SQLAlchemy
    models, enabling soft deletion functionality where records can be
    deactivated instead of physically removed from the database.

    Attributes:     is_active: Boolean flag indicating whether the
    record is active               (True) or soft-deleted (False)

    Note:     Default value is True, meaning new records are active by
    default.     This approach preserves data integrity and enables
    audit trails     while allowing record "deletion" from user
    perspective.
    """

    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
