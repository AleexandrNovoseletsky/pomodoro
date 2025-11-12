"""Ошибки ненахода пользователя."""


class UserNotFoundError(Exception):
    """Ошибка – пользователь не найден."""

    def __init__(self, phone: str | None = None):
        """Инициадизируем ошибку."""
        self.phone = phone

    def __str__(self):
        """Строковое представление ошибки."""
        return f" Пользователь {self.phone} не найден."
