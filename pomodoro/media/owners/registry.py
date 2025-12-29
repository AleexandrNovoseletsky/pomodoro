"""Media owner registry for managing file ownership relationships."""

import enum
from collections.abc import Callable
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from pomodoro.core.repositories.base_crud import ORMModel
from pomodoro.task.repositories.category import CategoryRepository
from pomodoro.task.repositories.tag import TagRepository
from pomodoro.task.repositories.task import TaskRepository
from pomodoro.user.repositories.user import UserRepository


class OwnerType(enum.StrEnum):
    """Which model the file belongs to."""

    USER = "user"
    TAG = "tag"
    TASK = "task"
    CATEGORY = "category"


class OwnerRepositoryProtocol(Protocol):
    """Protocol for owner repository interfaces."""

    async def get_one_object_or_raise(self, object_id: int) -> ORMModel:
        """Get owner object by ID or raise exception."""

OwnerRepoFactory = Callable[
    [async_sessionmaker[AsyncSession]],
    OwnerRepositoryProtocol,
]

OWNER_REPOSITORY_REGISTRY: dict[OwnerType, OwnerRepoFactory] = {
    OwnerType.TAG: lambda sm: TagRepository(sessionmaker=sm),
    OwnerType.TASK: lambda sm: TaskRepository(sessionmaker=sm),
    OwnerType.CATEGORY: lambda sm: CategoryRepository(sessionmaker=sm),
    OwnerType.USER: lambda sm: UserRepository(sessionmaker=sm),
}
