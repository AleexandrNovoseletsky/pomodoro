"""Сервисы пользователей."""

from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.services.media_service import MediaService
from pomodoro.user.models.users import UserProfile, UserRole
from pomodoro.user.permisiions import check_update_permissions
from pomodoro.user.repositories.user import UserRepository
from pomodoro.user.schemas.user import (
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
        media_service: MediaService,
    ):
        """Игициализируем сервис пользователей."""
        self.media_service = media_service
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
        # Проверяем есть ли у пользователя права на изминение
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
        # Проверяем есть ли у пользователя права на удаление
        target_user: ResponseUserProfileSchema = await super().get_one_object(
            object_id=user_id
        )
        await check_update_permissions(
            target_user=target_user, current_user=current_user
        )
        # Очищаем файлы
        await self.media_service.delete_all_by_owner(
            owner_type="task", owner_id=user_id
            )
        return await super().delete_object(object_id=user_id)
