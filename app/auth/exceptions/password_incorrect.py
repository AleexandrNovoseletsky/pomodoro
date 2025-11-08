class PasswordVerifyError(Exception):
    def __str__(self):
        return " Неверный пароль."
