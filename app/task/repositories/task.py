from sqlalchemy.ext.asyncio import AsyncSession

from app.task.models.tasks import Task
from app.core.repositories.base_crud import CRUDRepository


class TaskRepository(CRUDRepository):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session, Task)
