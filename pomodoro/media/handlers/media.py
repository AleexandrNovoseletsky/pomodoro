"""Роуты медиа."""

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile, status

from pomodoro.auth.dependencies.auth import require_roles
from pomodoro.media.dependencies.media import get_media_service
from pomodoro.media.models.files import OwnerType
from pomodoro.media.schemas.media import ResponseFileSchema
from pomodoro.media.services.media_service import MediaService
from pomodoro.user.dependencies.user import get_current_user
from pomodoro.user.schemas.user import ResponseUserProfileSchema

current_user_annotated = Annotated[
    ResponseUserProfileSchema, Depends(get_current_user)
]
media_service_annotated = Annotated[
        MediaService, Depends(dependency=get_media_service)
        ]
only_admin = Depends(
    dependency=require_roles(allowed_roles=("root", "admin"))
)
router = APIRouter()


@router.get(
        path="/{file_id}/url",
        response_model=dict,
        status_code=status.HTTP_200_OK,
        )
async def get_file_url(
    file_id: int,
    media_service: media_service_annotated,
):
    """Получить временную ссылку на файл."""
    url = await media_service.get_presigned_url(file_id=file_id)
    return {"url": url}


@router.get(
        path="/{file_id}",
        response_model=ResponseFileSchema,
        status_code=status.HTTP_200_OK,
        )
async def get_file(
    file_id: int,
    media_service: media_service_annotated,
):
    """Получение файла по ID."""
    return await media_service.get_one_object(object_id=file_id)


@router.get(
        path="/{domain}/{owner_id}",
        response_model=list[ResponseFileSchema],
        status_code=status.HTTP_200_OK,
        )
async def get_files_by_owner(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
):
    """получение всех файлов ресурса."""
    return await media_service.get_by_owner(domain=domain, owner_id=owner_id)


@router.post(
        path="/{domain}/{owner_id}/upload",
        response_model=ResponseFileSchema,
        status_code=status.HTTP_201_CREATED,
        )
async def upload_file(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
    current_user: current_user_annotated,
    file: Annotated[UploadFile, File(...)],
):
    """Загрузка файла в хранилище и сохранение в БД."""
    return await media_service.upload_file(
        file=file,
        domain=domain,
        owner_id=owner_id,
        current_user=current_user
    )


@router.post(
        path="/{domain}/{owner_id}/upload/multiple",
        response_model=list[ResponseFileSchema],
        status_code=status.HTTP_201_CREATED,
        )
async def upload_files(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
    current_user: current_user_annotated,
    files: Annotated[list[UploadFile], File(...)],
):
    """Множественная загрузка файлов."""
    files_to_schema = []
    semaphore = asyncio.Semaphore(5)  # максимум 5 параллельных загрузок

    async def sem_upload(file):
        async with semaphore:
            return await media_service.upload_file(
                file=file,
                current_user=current_user,
                domain=domain,
                owner_id=owner_id
            )

    tasks = [sem_upload(f) for f in files]
    files_to_schema = await asyncio.gather(*tasks)
    return files_to_schema


@router.patch(
        path="/{file_id}/make_primary",
        dependencies=[only_admin],
        response_model=ResponseFileSchema,
        status_code=status.HTTP_200_OK,
        )
async def make_primary(
    file_id: int,
    media_service: media_service_annotated,
):
    """Устанавливает файл как основной (primary) у ресурса."""
    return await media_service.set_primary(file_id=file_id)


@router.delete(
        path="/{file_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[only_admin],
        )
async def delete_file(
    file_id: int,
    media_service: media_service_annotated,
):
    """Удаление файла из хранилища и БД."""
    await media_service.delete_file(file_id=file_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/{domain}/{owner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[only_admin],
)
async def delete_files_by_owner(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
):
    """Удаляет все файлы ресурса."""
    await media_service.delete_all_by_owner(
        owner_type=domain, owner_id=owner_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
