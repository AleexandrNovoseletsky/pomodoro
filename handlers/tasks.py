from fastapi import APIRouter, Depends, status

from database.models import Tasks
from dependecy import get_task_service
from schemas.Task import CreateTaskSchema, ResponseTaskSchema
from services.task_service import TaskService

router = APIRouter(prefix='/tasks', tags=['tasks'])

@router.get('/', response_model=list[ResponseTaskSchema])
async def get_tasks(
    task_service: TaskService = Depends(get_task_service)
) -> list[ResponseTaskSchema]:
    return await task_service.get_all_tasks()

@router.post('/', response_model=ResponseTaskSchema)
async def create_task(
    task: CreateTaskSchema,
    task_service: TaskService = Depends(get_task_service)
) -> Tasks:
    return await task_service.create_task(task)

@router.patch('/', response_model=ResponseTaskSchema)
async def update_task(
    task_id: int,
    name: str,
    task_service: TaskService = Depends(get_task_service)
) -> Tasks:
    return await task_service.update_task_name(task_id, name)

@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(get_task_service)
) -> None:
    return await task_service.delete_task(task_id)
