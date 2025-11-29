"""User services.

Provides business logic layer for user operations including
registration, profile management, and administrative functions. Extends
base CRUD service with user-specific functionality including password
hashing, permission checks, and media cleanup.
"""

from pomodoro.auth.security import get_password_hash
from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.models.files import OwnerType
from pomodoro.media.services.media_service import MediaService
from pomodoro.user.models.users import UserProfile, UserRole
from pomodoro.user.permisiions import check_update_permissions
from pomodoro.user.repositories.user import UserRepository
from pomodoro.user.schemas.user import (
    CreateUserProfileORM,
    CreateUserProfileSchema,
    ResponseUserProfileSchema,
    UpdateUserProfileSchema,
)

# Role constants for permission management
admin = UserRole.ADMIN
root = UserRole.ROOT


class UserProfileService(CRUDService):
    """User service inheriting from base CRUD service.

    Extends base CRUD operations with user-specific business logic
    including password management, permission validation, and media
    cleanup.

    Attributes:     media_service: Media service instance for file
    operations     repository: User repository for data access
    response_schema: Response schema for data serialization
    """

    repository: UserRepository

    def __init__(
        self,
        user_repo: UserRepository,
        media_service: MediaService,
    ):
        """Initialize user service with dependencies.

        Args:     user_repo: User repository for data operations
        media_service: Media service for file management
        """
        self.media_service = media_service
        super().__init__(
            repository=user_repo, response_schema=ResponseUserProfileSchema
        )

    async def create_user(
        self, user_data: CreateUserProfileSchema
    ) -> ResponseUserProfileSchema:
        """Register new user with secure password handling.

        Processes user registration by securely hashing the password and
        creating a new user profile in the database.

        Args:     user_data: User registration data including plain text
        password

        Returns:     Newly created user profile with sensitive data
        excluded

        Note:     Plain text password is immediately hashed and removed
        from memory     for security best practices
        """
        hashed_password = get_password_hash(password=user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]

        new_user_data = CreateUserProfileORM(**user_dict)
        new_user = await self.repository.create_object(data=new_user_data)
        return new_user

    async def update_me(
        self, current_user: UserProfile, update_data: UpdateUserProfileSchema
    ) -> ResponseUserProfileSchema:
        """Update profile of the user who made the request.

        Allows users to update their own profile information without
        additional permission checks.

        Args:     current_user: Authenticated user making the request
        update_data: Partial profile data for update

        Returns:     Updated user profile
        """
        return await super().update_object(
            object_id=current_user.id, update_data=update_data
        )

    async def update_user(
        self,
        user_id: int,
        current_user: UserProfile,
        update_data: UpdateUserProfileSchema,
    ) -> ResponseUserProfileSchema:
        """Update user data with permission validation.

        Updates another user's profile after verifying the current user
        has appropriate permissions for the operation.

        Args:     user_id: Target user identifier to update
        current_user: Authenticated user making the request
        update_data: Partial profile data for update

        Returns:     Updated user profile

        Raises:     PermissionError: If current user lacks update
        permissions
        """
        target_user: ResponseUserProfileSchema = await super().get_one_object(
            object_id=user_id
        )
        # Verify user has permissions to update the target user
        await check_update_permissions(
            target_user=target_user, current_user=current_user
        )
        return await super().update_object(
            object_id=user_id, update_data=update_data
        )

    async def delete_user(
        self, user_id: int, current_user: UserProfile
    ) -> None:
        """Delete user with permission validation and media cleanup.

        Performs complete user deletion including: - Permission
        validation for deletion rights - Media file cleanup for user-
        owned content - Database record deletion

        Args:     user_id: Target user identifier to delete
        current_user: Authenticated user making the request

        Raises:     PermissionError: If current user lacks deletion
        permissions
        """
        # Verify user has permissions to delete the target user
        target_user: ResponseUserProfileSchema = await super().get_one_object(
            object_id=user_id
        )
        await check_update_permissions(
            target_user=target_user, current_user=current_user
        )
        # Clean up user-associated media files
        await self.media_service.delete_all_by_owner(
            domain=OwnerType.USER, owner_id=user_id
        )
        return await super().delete_object(object_id=user_id)
