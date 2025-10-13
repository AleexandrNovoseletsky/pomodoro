from sqlalchemy import select, delete, update
from sqlalchemy.orm import Session

from database import Categories, Tasks
from schemas.Task import CreateTaskSchema


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

    def delete_task(self, task_id: int) -> None:
        query = delete(Tasks).where(Tasks.id == task_id)
        with self.db_session() as session:
            session.execute(query)
            session.commit()

    def get_tasks_by_category_name(
            self, category_name: str
    ) -> list[Tasks]:

        with self.db_session() as session:
            query = (
                select(Tasks)
                .join(Categories, Tasks.category_id == Categories.id)
                .where(Categories.name == category_name)
            )
            tasks = session.execute(query).scalars().all()
            return tasks

    def update_task_name(self, task_id: int, name: str) -> CreateTaskSchema:
        query = update(Tasks).where(Tasks.id == task_id).values(
            name=name,
        )
        with self.db_session() as session:
            session.execute(query)
            session.commit()
            task = self.get_task(task_id)
            return task
