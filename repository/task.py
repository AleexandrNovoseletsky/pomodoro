from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database import Tasks
from schemas.Task import CreateTaskSchema, UpdateTaskSchema


class TaskRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_task(self, task_id: int) -> Tasks | None:
        query = select(Tasks).where(Tasks.id == task_id)
        with self.db_session() as session:
            task = session.execute(query).scalar_one_or_none()
            return task

    def get_tasks(self) -> list[Tasks]:
        query = select(Tasks)
        with self.db_session() as session:
            tasks = session.execute(query).scalars().all()
            return tasks

    def create_task(self, task: CreateTaskSchema) -> Tasks:
        task_orm = Tasks(
            name=task.name,
            pomodoro_count=task.pomodoro_count,
            category_id=task.category_id
        )
        with self.db_session() as session:
            session.add(task_orm)
            session.commit()
            session.refresh(task_orm)
            return task_orm

    def update_task(
            self,
            task_id: int,
            update_data: UpdateTaskSchema
    ) -> Tasks | None:
        query = select(Tasks).where(Tasks.id == task_id)
        with self.db_session() as session:
            task = session.execute(query).scalar_one_or_none()
            if task is None:
                return None
            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(task, key, value)
            session.commit()
            session.refresh(task)
            return task

    def delete_task(self, task_id: int) -> bool:
        query = delete(Tasks).where(Tasks.id == task_id)
        with self.db_session() as session:
            result = session.execute(query)
            session.commit()
            return result.rowcount > 0
