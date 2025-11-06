from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependencies import require_owner_or_roles, require_roles, get_task_resource
from dependencies import get_task_service, get_current_user
from models import Tasks
from schemas import CreateTaskSchema, ResponseTaskSchema, UpdateTaskSchema
from services import TaskService

current_user_annotated = Annotated[dict, Depends(get_current_user)]
owner_or_admin_depends = Depends(
    require_owner_or_roles(
        resource_getter=get_task_resource, allowed_roles=("root", "admin")
    )
)
router = APIRouter(prefix="/tasks", tags=["tasks"])
task_service_annotated = Annotated[TaskService, Depends(dependency=get_task_service)]


@router.get(path="/", response_model=list[ResponseTaskSchema])
async def get_tasks(
    task_service: task_service_annotated,
) -> list[ResponseTaskSchema]:
    return await task_service.get_all_objects()


@router.post(
    path="/",
    response_model=ResponseTaskSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(allowed_roles=("root", "admin", "user")))],
)
async def create_task(
    body: CreateTaskSchema,
    task_service: task_service_annotated,
    current_user: current_user_annotated,
) -> Tasks:
    return await task_service.create_object(current_user=current_user, object_data=body)


@router.patch(
    path="/",
    response_model=ResponseTaskSchema,
    dependencies=[owner_or_admin_depends],
)
async def update_task(
    task_id: int,
    body: UpdateTaskSchema,
    task_service: task_service_annotated,
    current_user: current_user_annotated,
):
    return await task_service.update_object(
        object_id=task_id,
        update_data=body,
        current_user=current_user,
    )


@router.delete(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[owner_or_admin_depends],
)
async def delete_task(
    task_id: int,
    task_service: task_service_annotated,
    current_user: current_user_annotated,
) -> None:
    return await task_service.delete_object(
        object_id=task_id, current_user=current_user
    )
