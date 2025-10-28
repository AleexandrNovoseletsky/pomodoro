from fastapi import APIRouter, Depends, status
from fastapi.params import Body

from auth.permissions import require_roles
from dependencies import get_task_service, get_current_user
from models import Tasks
from schemas import CreateTaskSchema, ResponseTaskSchema, UpdateTaskSchema
from services import TaskService

router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get(path='/', response_model=list[ResponseTaskSchema])
async def get_tasks(
    task_service: TaskService = Depends(get_task_service)
) -> list[ResponseTaskSchema]:
    return await task_service.get_all_objects()


@router.post(
    path='/',
    response_model=ResponseTaskSchema,
    dependencies=[Depends(require_roles('root', 'admin', 'user'))]
)
async def create_task(
    task: CreateTaskSchema,
        task_service: TaskService = Depends(get_task_service),
        current_user: dict = Depends(get_current_user),
) -> Tasks:
    return await task_service.create_object(
        current_user_data=current_user, object_data=task
    )


@router.patch(
    '/',
    response_model=ResponseTaskSchema,
    dependencies=[Depends(require_roles(
        'root', 'admin', 'user')
    )]
)
async def update_task(
        task_id: int,
        update_data: UpdateTaskSchema = Body(...),
        current_user: dict = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service),
):
    return await task_service.update_object(
        object_id=task_id,
        update_data=update_data,
        current_user=current_user,
    )


@router.delete(
    path='/',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles('root', 'admin', 'user'))]
)
async def delete_task(
        task_id: int,
        current_user: dict = Depends(get_current_user),
        task_service: TaskService = Depends(get_task_service)
) -> None:
    return await task_service.delete_object(task_id, current_user=current_user)
