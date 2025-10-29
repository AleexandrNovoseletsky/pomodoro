class ObjectNotFoundError(Exception):
    def __init__(self, object_id):
        self.object_id = object_id

    def __str__(self):
        return f" Объект с id={self.object_id} в базе не найден."
