"""Роуты мелиа."""

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, status

from pomodoro.auth.dependencies.auth import require_owner_or_roles
from pomodoro.media.dependencies.media import (
    get_media_resource,
    get_media_service,
)
from pomodoro.media.services.media_service import MediaService
from pomodoro.user.dependencies.user import get_current_user
from pomodoro.user.schemas.user import ResponseUserProfileSchema

current_user_annotated = Annotated[
    ResponseUserProfileSchema, Depends(get_current_user)
]
media_service_annotated = Annotated[
        MediaService, Depends(dependency=get_media_service)
        ]
# Проверка влдаельца ресурса, или роли пользователя сделавшего запрос
owner_or_admin_depends = Depends(
    require_owner_or_roles(
        resource_getter=get_media_resource, allowed_roles=("root", "admin")
    )
)
router = APIRouter()


@router.post("/upload/{domain}")
async def upload_media(
    domain: str,
    file: UploadFile,
    media_service: media_service_annotated,
    current_user: current_user_annotated,
):
    """агрузка файла в хранилище и сохранение в БД."""
    return await media_service.upload_file(
        file=file, domain=domain, current_user=current_user
        )


@router.delete(
        path="/{file_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[owner_or_admin_depends],
        )
async def delete_media(
    file_id: int,
    media_service: media_service_annotated,
):
    """даление файла из хранилища и БД."""
    return await media_service.delete_file(file_id=file_id)
