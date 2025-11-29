"""Checking the database restrictions.

Provides utilities for creating database-level constraints and
validations. Includes functions for generating SQL CHECK constraints
based on Python enums to ensure data integrity at the database level.
"""

import enum

from sqlalchemy import CheckConstraint


def make_check_in(
    enum_cls: type[enum.StrEnum], column_name: str
) -> CheckConstraint:
    """Create a SQL CHECK constraint for enum-based field validation.

    Generates a database-level CHECK constraint that restricts a column
    to only accept values defined in the specified enumeration class.
    This ensures data integrity at the database level, preventing
    invalid values from being inserted regardless of application logic.

    Args:     enum_cls: Enumeration class containing allowed string
    values     column_name: Name of the database column to apply
    constraint to

    Returns:     SQLAlchemy CheckConstraint instance for table
    configuration

    Example:     __table_args__ = (make_check_in(UserRole, 'role'),)

    Note:     The constraint is enforced at the database level,
    providing     an additional layer of data integrity beyond
    application validation
    """
    values = ", ".join(f"'{e.value}'" for e in enum_cls)
    return CheckConstraint(
        sqltext=f"{column_name} IN ({values})", name=f"check_{column_name}"
    )
