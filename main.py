from fastapi import FastAPI

from custom_exceptions.base import AppException
from custom_exceptions.handlers import app_exception_handler, default_exception_handler
from handlers import routers


app = FastAPI()

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, default_exception_handler)

for router in routers:
    app.include_router(router)
