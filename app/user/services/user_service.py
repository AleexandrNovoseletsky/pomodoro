"""Сервисы пользователей."""

from app.core.services.base_crud import CRUDService
from app.user.models.users import UserProfile, UserRole
from app.user.permisiions import check_update_permissions
from app.user.repositories.user import UserRepository
from app.user.schemas.user import (
    ResponseUserProfileSchema,
    UpdateUserProfileSchema,
)

admin = UserRole.ADMIN
root = UserRole.ROOT


class UserProfileService(CRUDService):
    """Сервис пользователей. Унаследован от базового сервиса."""

    repository: UserRepository

    def __init__(
        self,
        user_repo: UserRepository,
    ):
        """Игициализируем сервис пользователей."""
        super().__init__(
            repository=user_repo, response_schema=ResponseUserProfileSchema
        )

    async def update_me(
        self, current_user: UserProfile, update_data: UpdateUserProfileSchema
    ) -> ResponseUserProfileSchema:
        """Обновление данных пользователя сделавшего запрос."""
        return await super().update_object(
            object_id=current_user.id, update_data=update_data
        )

    async def update_user(
        self,
        user_id: int,
        current_user: UserProfile,
        update_data: UpdateUserProfileSchema,
    ) -> ResponseUserProfileSchema:
        """Обновление даных пользователя."""
        target_user: ResponseUserProfileSchema = await super().get_one_object(
            object_id=user_id
        )

        await check_update_permissions(
            target_user=target_user, current_user=current_user
        )
        return await super().update_object(
            object_id=user_id, update_data=update_data
        )

    async def delete_user(
            self, user_id: int, current_user: UserProfile
            ) -> None:
        """Удаление пользователя."""
        target_user: ResponseUserProfileSchema = await super().get_one_object(
            object_id=user_id
        )
        await check_update_permissions(
            target_user=target_user, current_user=current_user
        )
        return await super().delete_object(object_id=user_id)
