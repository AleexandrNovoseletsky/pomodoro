from fastapi import APIRouter, Depends, status

from database.models import Tasks
from dependecy import get_task_repository, get_cache_task_repository
from schemas.Task import CreateTaskSchema, ResponseTaskSchema

router = APIRouter(prefix='/tasks', tags=['tasks'])

@router.get('/', response_model=list[ResponseTaskSchema])
async def get_tasks(
        repo = Depends(get_task_repository),
        cache_repo = Depends(get_cache_task_repository)
) -> list[ResponseTaskSchema]:
    cache_tasks = await cache_repo.get_all_tasks()
    if cache_tasks:
        return cache_tasks
    else:
        db_tasks = repo.get_tasks()
        task_schema = [
            ResponseTaskSchema.model_validate(task) for task in db_tasks
        ]
        await cache_repo.set_all_tasks(task_schema)
        return task_schema

@router.post('/', response_model=ResponseTaskSchema)
async def create_task(
        task: CreateTaskSchema,
        repo = Depends(get_task_repository)
) -> Tasks:
    return repo.create_task(task)

@router.patch('/', response_model=ResponseTaskSchema)
async def update_task(
        task_id: int,
        name: str,
        repo = Depends(get_task_repository)
) -> Tasks:
    return repo.update_task_name(task_id, name)

@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        repo = Depends(get_task_repository)
) -> None:
    return repo.delete_task(task_id)
