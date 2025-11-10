from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from app.auth.dependencies.auth import get_auth_service
from app.auth.services.auth import AuthService

router = APIRouter()

auth_service_annotated = Annotated[
    AuthService, Depends(dependency=get_auth_service)
]


@router.get(path="/login/yandex")
async def yandex_login(auth_service: auth_service_annotated):
    redirect_url = await auth_service.get_yandex_redirect_url()
    print(redirect_url)
    return RedirectResponse(url=redirect_url)


@router.get(path="/yandex")
async def yandex_auth(code: str, auth_service: auth_service_annotated):
    return await auth_service.get_yandex_auth(code=code)
