from app.core.services.base_crud import CRUDService
from app.user.models.users import UserProfile, UserRole
from app.user.permisiions import check_permissions
from app.user.repositories.user import UserRepository
from app.user.schemas.user import (
    ResponseUserProfileSchema,
    UpdateUserProfileSchema,
)

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

        await check_permissions(
            target_user=target_user, current_user=current_user
        )
        return await super().update_object(
            object_id=user_id, update_data=update_data
        )

    async def delete_user(self, user_id: int, current_user: UserProfile):
        target_user: ResponseUserProfileSchema = await super().get_one_object(
            object_id=user_id
        )
        await check_permissions(
            target_user=target_user, current_user=current_user
        )
        return await super().delete_object(object_id=user_id)
