import enum

from sqlalchemy import CheckConstraint


def make_check_in(
    enum_cls: type[enum.StrEnum], column_name: str
) -> CheckConstraint:
    """
    Создаёт SQL CHECK constraint для поля, ограниченного значениями enum.

    Args:
        enum_cls: класс перечисления (наследник enum.StrEnum)
        column_name: имя поля в таблице

    Returns:
        sqlalchemy.CheckConstraint
    """
    values = ", ".join(f"'{e.value}'" for e in enum_cls)
    return CheckConstraint(
        f"{column_name} IN ({values})", name=f"check_{column_name}"
    )
