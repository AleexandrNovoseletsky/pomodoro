"""Формы авторизации."""

from fastapi import Form


class LoginForm:
    """Форма входа пользователя."""

    def __init__(
        self,
        phone: str = Form(..., alias="username"),
        password: str = Form(...),
    ):
        """Инициализируем форму."""
        self.phone = phone
        self.password = password
