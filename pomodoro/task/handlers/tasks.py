"""HTTP-роуты для работы с задачами (tasks).

Роуты используют зависимости для авторизации и получения сервисов.
Префиксы для роутов задаются в `pomodoro.main`.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from pomodoro.auth.dependencies.auth import require_owner_or_roles
from pomodoro.task.dependencies.task import get_task_resource, get_task_service
from pomodoro.task.schemas.task import (
    CreateTaskORM,
    CreateTaskSchema,
    ResponseTaskSchema,
    UpdateTaskSchema,
)
from pomodoro.task.services.task_service import TaskService
from pomodoro.user.dependencies.user import get_current_user
from pomodoro.user.schemas.user import ResponseUserProfileSchema

# Пользователь сделавший запрос
current_user_annotated = Annotated[
    ResponseUserProfileSchema, Depends(get_current_user)
]
# Проверка влдаельца ресурса, или роли пользователя сделавшего запрос
owner_or_admin_depends = Depends(
    require_owner_or_roles(
        resource_getter=get_task_resource, allowed_roles=("root", "admin")
    )
)
# Аннотированная зависимость получения сервиса задач
task_service_annotated = Annotated[
    TaskService, Depends(dependency=get_task_service)
]

router = APIRouter()


@router.get(path="/", response_model=list[ResponseTaskSchema])
async def get_tasks(
    task_service: task_service_annotated,
) -> list[ResponseTaskSchema]:
    """Получить все задачи. Доступно всем."""
    return await task_service.get_all_objects()


@router.post(
    path="/",
    response_model=ResponseTaskSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    body: CreateTaskSchema,
    task_service: task_service_annotated,
    current_user: current_user_annotated,
) -> ResponseTaskSchema:
    """Создать здачу. Доступно авторизованному пользователю."""
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
) -> ResponseTaskSchema:
    """Изменить задачу. Доступно владельцу и администратору."""
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
    """Удалить задачу. Доступно владельцу и администратору."""
    return await task_service.delete_object(object_id=task_id)
