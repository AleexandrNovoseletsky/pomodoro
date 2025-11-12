"""HTTP-роуты для работы с задачами (tasks).

Роуты используют зависимости для авторизации и получения сервисов.
Префиксы для роутов задаются в `app.main`.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies.auth import (
    require_owner_or_roles,
    require_roles,
)
from app.task.dependencies.task import get_task_resource, get_task_service
from app.user.dependencies.user import get_current_user
from app.task.schemas.task import (
    CreateTaskSchema,
    CreateTaskORM,
    ResponseTaskSchema,
    UpdateTaskSchema,
)
from app.user.schemas.user import ResponseUserProfileSchema
from app.task.services.task_service import TaskService

current_user_annotated = Annotated[
    ResponseUserProfileSchema, Depends(get_current_user)
]
owner_or_admin_depends = Depends(
    require_owner_or_roles(
        resource_getter=get_task_resource, allowed_roles=("root", "admin")
    )
)
router = APIRouter()
task_service_annotated = Annotated[
    TaskService, Depends(dependency=get_task_service)
]


@router.get(path="/", response_model=list[ResponseTaskSchema])
async def get_tasks(
    task_service: task_service_annotated,
) -> list[ResponseTaskSchema]:
    return await task_service.get_all_objects()


@router.post(
    path="/",
    response_model=ResponseTaskSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_roles(allowed_roles=("root", "admin", "user")))
    ],
)
async def create_task(
    body: CreateTaskSchema,
    task_service: task_service_annotated,
    current_user: current_user_annotated,
) -> ResponseTaskSchema:
    create_task_orm = CreateTaskORM(
        **body.model_dump(), author_id=current_user.id
    )
    return await task_service.create_object_with_author(
        current_user=current_user, object_data=create_task_orm
    )


@router.patch(
    path="/{task_id}",
    response_model=ResponseTaskSchema,
    dependencies=[owner_or_admin_depends],
)
async def update_task(
    task_id: int, body: UpdateTaskSchema, task_service: task_service_annotated
):
    return await task_service.update_object(
        object_id=task_id, update_data=body
    )


@router.delete(
    path="/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[owner_or_admin_depends],
)
async def delete_task(
    task_id: int, task_service: task_service_annotated
) -> None:
    return await task_service.delete_object(object_id=task_id)
