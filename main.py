from fastapi import FastAPI, Request
from sqlalchemy.exc import IntegrityError

from handlers import routers
from services.integrity_exception_service import IntegrityExceptionService

app = FastAPI()

for router in routers:
    app.include_router(router)

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    service = IntegrityExceptionService(exc)
    return service.get_json_to_exception()