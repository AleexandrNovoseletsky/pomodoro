class AccessDenied(Exception):
    def __str__(self):
        return f' Доступ запрещён.'
