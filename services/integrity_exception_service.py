from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class IntegrityExceptionService:
    def __init__(self, exc: IntegrityError) -> None:
        self.error_message = str(exc.orig).lower()

    def get_json_to_exception(self) -> JSONResponse:
        if 'unique constraint' in self.error_message:
            return JSONResponse(
                status_code=409,
                content={
                    'detail': 'Объект с таким уникальным значением уже существует.',
                    'error': self.error_message
                }
            )
        if 'duplicate key value' in self.error_message:
            return JSONResponse(
                status_code=409,
                content={
                    'detail': 'Объект с таким уникальным ключом уже существует.',
                    'error': self.error_message
                }
            )
        if 'not-null constraint' in self.error_message:
            return JSONResponse(
                status_code=400,
                content={
                    'detail': 'Одно из обязательных полей не может быть пустым.',
                    'error': self.error_message
                }
            )
        if 'foreign key constraint' in self.error_message:
            return JSONResponse(
                status_code=400,
                content={
                    'detail': 'Ссылка на несуществующую запись. Проверьте foreign key.',
                    'error': self.error_message
                }
            )

        return JSONResponse(
            status_code=400,
            content={"detail": "Ошибка целостности данных базы."}
        )
