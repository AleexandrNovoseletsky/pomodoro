from sqlalchemy.orm import Session

from models import Task
from repositories.base_crud import CRUDRepository


class TaskRepository(CRUDRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Task)
