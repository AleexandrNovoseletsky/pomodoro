"""Media edpoints."""

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, File, Response, UploadFile, status

from pomodoro.auth.dependencies.auth import require_roles
from pomodoro.media.dependencies.media import get_media_service
from pomodoro.media.models.files import OwnerType
from pomodoro.media.schemas.media import ResponseFileSchema
from pomodoro.media.services.media_service import MediaService
from pomodoro.user.dependencies.user import get_current_user
from pomodoro.user.models.users import UserProfile, UserRole

current_user_annotated = Annotated[UserProfile, Depends(get_current_user)]
media_service_annotated = Annotated[
    MediaService, Depends(dependency=get_media_service)
]
only_admin = Depends(
    dependency=require_roles(allowed_roles=(UserRole.ROOT, UserRole.ADMIN))
)
router = APIRouter()


@router.get(
    path="/{file_id}/url",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Получить ссылку на файл",
)
async def get_file_url(
    file_id: int,
    media_service: media_service_annotated,
):
    """Get a temporary link to the file.

    Args:
        file_id: The ID of the file we are linking to.
        media_service: Depends on media service.

    Returns:
        Dict {"url": url}
    """
    url = await media_service.get_presigned_url(file_id=file_id)
    return {"url": url}


@router.get(
    path="/{file_id}",
    response_model=ResponseFileSchema,
    status_code=status.HTTP_200_OK,
    summary="Получить файл по ID.",
)
async def get_file(
    file_id: int,
    media_service: media_service_annotated,
):
    """Getting a file by ID.

    Args:
        file_id: ID of the file you are looking for.
        media_service: Depends on media service.

    Returns:
        Response file schemes validated by Pydantic.
    """
    return await media_service.get_one_object(object_id=file_id)


@router.get(
    path="/{domain}/{owner_id}",
    response_model=list[ResponseFileSchema],
    status_code=status.HTTP_200_OK,
    summary="Получить все файлы ресурса",
)
async def get_files_by_owner(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
):
    """Getting all the resource files.

    Args:
        domain: Owner type. Example Task.
        owner_id: Resource ID. Example Task where id = 10.
        media_service: Depends on media service.

    Returns:
        List of response file schemes validated by Pydantic.
    """
    return await media_service.get_by_owner(domain=domain, owner_id=owner_id)


@router.post(
    path="/{domain}/{owner_id}/upload",
    response_model=ResponseFileSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Загрузить один файл",
)
async def upload_file(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
    current_user: current_user_annotated,
    file: Annotated[UploadFile, File(...)],
):
    """Uploading a file to the storage and saving it to the database.

    Args:
        domain: Owner type. Example Task.
        owner_id: Resource ID. Example Task where id = 10.
        media_service: Depends on media service.
        current_user: The user who made the request.
        file: uploaded file.

    Returns:
        Response file schemes validated by Pydantic.
    """
    return await media_service.upload_file(
        file=file, domain=domain, owner_id=owner_id, current_user=current_user
    )


@router.post(
    path="/{domain}/{owner_id}/upload/multiple",
    response_model=list[ResponseFileSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка нескольких файлов",
)
async def upload_files(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
    current_user: current_user_annotated,
    files: Annotated[list[UploadFile], File(...)],
):
    """Multiple file uploads.

    Args:
        domain: Owner type. Example Task.
        owner_id: Resource ID. Example Task where id = 10.
        media_service: Depends on media service.
        current_user: The user who made the request.
        files: uploaded files.

    Returns:
        List of response file schemes validated by Pydantic.
    """
    semaphore = asyncio.Semaphore(5)  # Maximum of 5 parallel uploads

    async def sem_upload(file):
        async with semaphore:
            return await media_service.upload_file(
                file=file,
                current_user=current_user,
                domain=domain,
                owner_id=owner_id,
            )

    tasks = [sem_upload(f) for f in files]
    files_to_schema = await asyncio.gather(*tasks)
    return files_to_schema


@router.post(
    path="/{domain}/{owner_id}/upload/image",
    response_model=list[ResponseFileSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка одного изображения",
    description="Создаётся три варианта изображения: "
    "ORIGINAL (Оригинальный размер), "
    "SMALL (Сжатое изображение), "
    "THUMB. (Сильно сжатое изображение)",
)
async def upload_image(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
    current_user: current_user_annotated,
    image: Annotated[UploadFile, File(...)],
):
    """Uploading a file to the storage and saving it to the database.

    Args:
        domain: Owner type. Example Task.
        owner_id: Resource ID. Example Task where id = 10.
        media_service: Depends on media service.
        current_user: The user who made the request.
        image: uploaded image.

    Returns:
        Response file schemes validated by Pydantic.
    """
    return await media_service.upload_image(
        image=image,
        domain=domain,
        owner_id=owner_id,
        current_user=current_user,
    )


@router.post(
    path="/{domain}/{owner_id}/upload/image/multiple",
    response_model=list[ResponseFileSchema],
    status_code=status.HTTP_201_CREATED,
    summary="Загрузка нескольких изображений",
    description="Создаётся три варианта каждого изображения: "
    "ORIGINAL (Оригинальный размер), "
    "SMALL (Сжатое изображение), "
    "THUMB. (Сильно сжатое изображение)",
)
async def upload_image(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
    current_user: current_user_annotated,
    images: Annotated[list[UploadFile], File(...)],
):
    """Uploading a file to the storage and saving it to the database.

    Args:
        domain: Owner type. Example Task.
        owner_id: Resource ID. Example Task where id = 10.
        media_service: Depends on media service.
        current_user: The user who made the request.
        images: uploaded images.

    Returns:
        Response file schemes validated by Pydantic.
    """
    semaphore = asyncio.Semaphore(5)  # Maximum of 5 parallel uploads

    async def sem_upload(image):
        async with semaphore:
            return await media_service.upload_image(
                image=image,
                domain=domain,
                owner_id=owner_id,
                current_user=current_user,
            )

    tasks = [sem_upload(f) for f in images]
    images_to_schema = await asyncio.gather(*tasks)

    # flatten list[list[ResponseFileSchema]] -> list[ResponseFileSchema]
    return [image for group in images_to_schema for image in group]


@router.patch(
    path="/{file_id}/make_primary",
    dependencies=[only_admin],
    response_model=ResponseFileSchema,
    status_code=status.HTTP_200_OK,
    summary="Установить файл как главный (primary) у ресурса",
)
async def make_primary(
    file_id: int,
    media_service: media_service_annotated,
):
    """Sets the file as the primary of the resource.

    Args:
        file_id: ID of the file that we make the primary.
        media_service: Depends on media service.

    Returns:
        Response file schemes validated by Pydantic.
    """
    return await media_service.set_primary(file_id=file_id)


@router.delete(
    path="/delete_orphans",
    status_code=status.HTTP_200_OK,
    dependencies=[only_admin],
    summary="Удалить осиротевшие файлы из хранилища и БД",
    description="Удаляет файлы которые есть в БД, но нет в хранилище. "
                "И наоборот, файлы которые есть в хранилище но нет в БД."
)
async def delete_orphaned_files(media_service: media_service_annotated):
    """Delete all orphaned files.

    Args:
        media_service: Depends on media service.

    Returns:
        Dict {
            "s3_deleted": 0
            "DB_deleted": 0
        }
    """
    s3_count = await media_service.delete_orphaned_files_on_storage()
    db_count = await media_service.delete_orphaned_files_on_db()
    return {"s3_deleted": s3_count, "DB_deleted": db_count}


@router.delete(
    path="/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[only_admin],
    summary="Удалить один файл",
)
async def delete_file(
    file_id: int,
    media_service: media_service_annotated,
):
    """Deleting a file from storage and database.

    Args:
        file_id: ID of the file to delete.
        media_service: Depends on media service.

    Returns:
        ''None''.
    """
    await media_service.delete_file(file_id=file_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/{domain}/{owner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[only_admin],
    summary="Удалить все файлы указанного ресурса",
)
async def delete_files_by_owner(
    domain: OwnerType,
    owner_id: int,
    media_service: media_service_annotated,
):
    """Deletes all resource files.

    Args:
        domain: Owner type. Example Task.
        owner_id: Resource ID. Example Task where id = 10.
        media_service: Depends on media service.

    Returns:
        ''None''
    """
    await media_service.delete_all_by_owner(domain=domain, owner_id=owner_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
