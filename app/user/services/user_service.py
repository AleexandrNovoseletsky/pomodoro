from app.core.exceptions.acces_denied import AccessDenied
from app.user.models.users import UserProfile, UserRole
from app.user.repositories.user import UserRepository
from app.user.schemas.user import (
    ResponseUserProfileSchema,
    UpdateUserProfileSchema,
)
from app.core.services.base_crud import CRUDService


admin = UserRole.ADMIN
root = UserRole.ROOT


class UserProfileService(CRUDService):
    repository: UserRepository

    def __init__(
        self,
        user_repo: UserRepository,
    ):
        super().__init__(
            repository=user_repo, response_schema=ResponseUserProfileSchema
        )

    async def update_me(
        self, current_user: UserProfile, update_data: UpdateUserProfileSchema
    ):
        return await super().update_object(
            object_id=current_user.id, update_data=update_data
        )

    async def update_user(
        self,
        user_id: int,
        current_user: UserProfile,
        update_data: UpdateUserProfileSchema,
    ):
        target_user: ResponseUserProfileSchema = await super().get_one_object(
            object_id=user_id
        )

        # 1. Рут не может быть изменён никем, кроме себя
        if (
            target_user.role == UserRole.ROOT
            and current_user.id != target_user.id
        ):
            raise AccessDenied()

        # 2. Админа может обновить только он сам или рут
        if target_user.role == UserRole.ADMIN:
            if current_user.role not in (UserRole.ROOT, UserRole.ADMIN):
                raise AccessDenied()
            if (
                current_user.id != target_user.id
                and current_user.role != UserRole.ROOT
            ):
                raise AccessDenied("Admin cannot update another admin.")

        return await super().update_object(
            object_id=user_id, update_data=update_data
        )
