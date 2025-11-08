class UserNotFoundError(Exception):
    def __init__(self, phone):
        self.phone = phone

    def __str__(self):
        return f" Пользователь с телефоном {self.phone} не зарегистрирован."
