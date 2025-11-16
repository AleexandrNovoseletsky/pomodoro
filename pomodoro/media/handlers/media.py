"""Media file management endpoints."""

import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Response,
    UploadFile,
    status,
)

from pomodoro.auth.dependencies.auth import require_roles
from pomodoro.media.dependencies.media import get_media_service
from pomodoro.media.models.files import OwnerType
from pomodoro.media.schemas.media import ResponseFileSchema
from pomodoro.media.services.media_service import MediaService
from pomodoro.user.dependencies.user import get_current_user
from pomodoro.user.schemas.user import ResponseUserProfileSchema

router = APIRouter()

CurrentUserDep = Annotated[
    ResponseUserProfileSchema, Depends(get_current_user)
]
MediaServiceDep = Annotated[MediaService, Depends(get_media_service)]
AdminOnly = Depends(require_roles(allowed_roles=("root", "admin")))

logger = logging.getLogger(__name__)


@router.get(
    path="/{file_id}/url",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_file_url(
    file_id: int,
    media_service: MediaServiceDep,
) -> dict:
    """Get temporary presigned URL for file download.

    Args:
        file_id: File ID.
        media_service: Media service instance.

    Returns:
        Dictionary with 'url' key containing presigned URL.
    """
    url = await media_service.get_presigned_url(file_id=file_id)
    return {"url": url}


@router.get(
    path="/{file_id}",
    response_model=ResponseFileSchema,
    status_code=status.HTTP_200_OK,
)
async def get_file(
    file_id: int,
    media_service: MediaServiceDep,
) -> ResponseFileSchema:
    """Get file metadata by ID.

    Args:
        file_id: File ID.
        media_service: Media service instance.

    Returns:
        File schema with metadata.
    """
    return await media_service.get_one_object(object_id=file_id)


@router.get(
    path="/{domain}/{owner_id}",
    response_model=list[ResponseFileSchema],
    status_code=status.HTTP_200_OK,
)
async def get_files_by_owner(
    domain: OwnerType,
    owner_id: int,
    media_service: MediaServiceDep,
) -> list[ResponseFileSchema]:
    """Get all files for an owner.

    Args:
        domain: Owner type (user/task/category).
        owner_id: ID of the owner.
        media_service: Media service instance.

    Returns:
        List of file schemas.
    """
    return await media_service.get_by_owner(
        domain=domain, owner_id=owner_id
    )


@router.post(
    path="/{domain}/{owner_id}/upload/file",
    response_model=ResponseFileSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    domain: OwnerType,
    owner_id: int,
    media_service: MediaServiceDep,
    current_user: CurrentUserDep,
    file: Annotated[UploadFile, File(...)],
) -> ResponseFileSchema:
    """Upload single file.

    Args:
        domain: Owner type (user/task/category).
        owner_id: ID of the owner.
        media_service: Media service instance.
        current_user: Current authenticated user.
        file: File to upload.

    Returns:
        File schema with DB metadata.
    """
    return await media_service.upload_file(
        file=file,
        domain=domain,
        owner_id=owner_id,
        current_user=current_user,
    )


@router.post(
    path="/{domain}/{owner_id}/upload/multiple/file",
    response_model=list[ResponseFileSchema],
    status_code=status.HTTP_201_CREATED,
)
async def upload_files(
    domain: OwnerType,
    owner_id: int,
    media_service: MediaServiceDep,
    current_user: CurrentUserDep,
    files: Annotated[list[UploadFile], File(...)],
) -> list[ResponseFileSchema]:
    """Upload multiple files concurrently.

    Args:
        domain: Owner type.
        owner_id: ID of the owner.
        media_service: Media service instance.
        current_user: Current authenticated user.
        files: List of files to upload.

    Returns:
        List of file schemas.
    """
    return await media_service.upload_files(
        files, current_user, domain, owner_id
    )


@router.post(
    path="/{domain}/{owner_id}/upload/image",
    response_model=list[ResponseFileSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[AdminOnly],
)
async def upload_image(
    domain: OwnerType,
    owner_id: int,
    media_service: MediaServiceDep,
    current_user: CurrentUserDep,
    file: Annotated[UploadFile, File(...)],
) -> list[ResponseFileSchema]:
    """Upload image with automatic WebP variant generation.

    Generates three variants: original, small thumbnail, and tiny
    thumbnail. Requires admin role.

    Args:
        domain: Owner type.
        owner_id: ID of the owner.
        media_service: Media service instance.
        current_user: Current authenticated user.
        file: Image file to upload.

    Returns:
        List of file schemas for each variant.
    """
    return await media_service.upload_image(
        file=file,
        current_user=current_user,
        domain=domain,
        owner_id=owner_id,
    )


@router.patch(
    path="/{file_id}/make_primary",
    response_model=ResponseFileSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[AdminOnly],
)
async def make_primary(
    file_id: int,
    media_service: MediaServiceDep,
) -> ResponseFileSchema:
    """Mark file as primary for its owner.

    Only admin users can perform this action.

    Args:
        file_id: File ID to set as primary.
        media_service: Media service instance.

    Returns:
        Updated file schema.
    """
    return await media_service.set_primary(file_id=file_id)


@router.delete(
    path="/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[AdminOnly],
)
async def delete_file(
    file_id: int,
    media_service: MediaServiceDep,
) -> Response:
    """Delete file from storage and database.

    Args:
        file_id: File ID to delete.
        media_service: Media service instance.

    Returns:
        Empty 204 response.
    """
    await media_service.delete_file(file_id=file_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    path="/{domain}/{owner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[AdminOnly],
)
async def delete_files_by_owner(
    domain: OwnerType,
    owner_id: int,
    media_service: MediaServiceDep,
) -> Response:
    """Delete all files for an owner.

    Args:
        domain: Owner type.
        owner_id: ID of the owner.
        media_service: Media service instance.

    Returns:
        Empty 204 response.
    """
    await media_service.delete_all_by_owner(
        owner_type=domain, owner_id=owner_id
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
