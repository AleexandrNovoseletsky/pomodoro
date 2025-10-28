class PasswordVerifyError(Exception):
    def __str__(self):
        return f' Неверный пароль.'
