"""HTTP routes for tasks.

Routes use dependencies for authorization and service injection.
Route prefixes are configured in `pomodoro.main`.
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
from pomodoro.user.models.users import UserProfile, UserRole

# User who made the request
current_user_annotated = Annotated[UserProfile, Depends(get_current_user)]

# Check if user is resource owner or has admin roles
root = UserRole.ROOT
admin = UserRole.ADMIN
owner_or_admin_depends = Depends(
    dependency=require_owner_or_roles(
        resource_getter=get_task_resource, allowed_roles=(root, admin)
    )
)

# Annotated dependency for task service injection
task_service_annotated = Annotated[
    TaskService, Depends(dependency=get_task_service)
]

router = APIRouter()


@router.get(
    path="/",
    response_model=list[ResponseTaskSchema],
    summary="Получить все задачи",
    description=("Возвращает список всех задач в системе. "
                 "Доступно всем пользователям."),
)
async def get_tasks(
    task_service: task_service_annotated,
) -> list[ResponseTaskSchema]:
    """Retrieve all tasks from the system.

    Fetches complete list of tasks with caching support for performance.
    Available to all authenticated users regardless of role.

    Args:
        task_service: Depends on task service

    Returns:
        List of validated task response schemas
    """
    return await task_service.get_all_objects()


@router.post(
    path="/",
    response_model=ResponseTaskSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Создать задачу",
    description=("Создание новой задачи в системе. "
                 "Доступно авторизованным пользователям."),
)
async def create_task(
    body: CreateTaskSchema,
    task_service: task_service_annotated,
    current_user: current_user_annotated,
) -> ResponseTaskSchema:
    """Create a new task in the system.

    Creates a task with the current user as author and automatically
    handles category assignment and validation.

    Args:
        body: Task creation data with name, pomodoro count, and category
        task_service: Depends on task service
        current_user: Authenticated user who will be set as task author

    Returns:
        Newly created task with system-generated fields
    """
    create_task_orm = CreateTaskORM(
        **body.model_dump(), author_id=current_user.id
    )
    return await task_service.create_object(object_data=create_task_orm)


@router.patch(
    path="/{task_id}",
    response_model=ResponseTaskSchema,
    dependencies=[owner_or_admin_depends],
    summary="Обновить задачу",
    description=("Изменение существующей задачи. "
                 "Доступно владельцу задачи и администраторам.")
)
async def update_task(
    task_id: int, body: UpdateTaskSchema, task_service: task_service_annotated
) -> ResponseTaskSchema:
    """Update an existing task with partial data.

    Allows modification of task properties with proper authorization
    checks. Only task owners and administrators can update tasks.

    Args:
        task_id: Unique identifier of the task to update
        body: Partial task data for update operation
        task_service: Depends on task service

    Returns:
        Updated task with modified fields

    Raises:
        ObjectNotFoundError: If task with specified ID doesn't exist
        AccessDenied: If user lacks ownership or administrative privileges
    """
    return await task_service.update_object(
        object_id=task_id, update_data=body
    )


@router.delete(
    path="/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[owner_or_admin_depends],
    summary="Удалить задачу",
    description=("Удаление задачи из системы. "
                 "Доступно владельцу задачи и администраторам.")
)
async def delete_task(
    task_id: int, task_service: task_service_annotated
) -> None:
    """Permanently delete a task from the system.

    Performs complete task deletion including associated media files
    and cache invalidation. Requires ownership or admin privileges.

    Args:
        task_id: Unique identifier of the task to delete
        task_service: Depends on task service

    Raises:
        ObjectNotFoundError: If task with specified ID doesn't exist
        AccessDenied: If user lacks ownership or administrative privileges
    """
    return await task_service.delete_object(object_id=task_id)
