"""User services.

Provides business logic layer for user operations including
registration, profile management, and administrative functions. Extends
base CRUD service with user-specific functionality including password
hashing, permission checks, and media cleanup.
"""
import secrets
import uuid

from pomodoro.auth.exceptions.password_incorrect import PasswordVerifyError
from pomodoro.auth.security import get_password_hash, verify_password
from pomodoro.core.email.service import EmailService
from pomodoro.core.exceptions.conflicts import PasswordAlreadySetError
from pomodoro.core.exceptions.invalid_reset_token import InvalidResetToken
from pomodoro.core.services.base_crud import CRUDService
from pomodoro.media.models.files import OwnerType
from pomodoro.media.services.media_service import MediaService
from pomodoro.user.models.users import UserProfile, UserRole
from pomodoro.user.permisiions import check_update_permissions
from pomodoro.user.repositories.cache_user import UserCacheRepository
from pomodoro.user.repositories.user import UserRepository
from pomodoro.user.schemas.user import (
    ChangePasswordSchema,
    CreateUserProfileORM,
    CreateUserProfileSchema,
    ResponseUserProfileSchema,
    SetPasswordSchema,
    UpdatePasswordORMSchema,
    UpdateUserProfileSchema,
)

# Role constants for permission management
admin = UserRole.ADMIN
root = UserRole.ROOT


class UserProfileService(
    CRUDService[ResponseUserProfileSchema]
):
    """User service inheriting from base CRUD service.

    Extends base CRUD operations with user-specific business logic
    including password management, permission validation, and media
    cleanup.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        cache_repo: UserCacheRepository,
        media_service: MediaService,
        email_service: EmailService
    ):
        """Initialize user service with dependencies.

        Args:
            user_repo: User repository for data operations
            cache_repo: Cache user repository
            media_service: Media service for file management
            email_service: Service for working with email
        """
        self.media_service = media_service
        self.cache_repo = cache_repo
        self.user_repo = user_repo
        self.email_service = email_service
        super().__init__(
            repository=user_repo, response_schema=ResponseUserProfileSchema
        )

    async def create_user(
        self, user_data: CreateUserProfileSchema
    ) -> ResponseUserProfileSchema:
        """Register new user with secure password handling.

        Processes user registration by securely hashing the password and
        creating a new user profile in the database.

        Args:
            user_data: User registration data including plain text
                       password

        Returns:
            Newly created user profile with sensitive data
            excluded

        Note:
            - Plain text password is immediately hashed and removed
              from memory for security best practices
        """
        hashed_password = get_password_hash(password=user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]

        new_user_data = CreateUserProfileORM(**user_dict)
        new_user = await super().create_object(object_data=new_user_data)
        return new_user

    async def update_me(
        self, current_user: UserProfile, update_data: UpdateUserProfileSchema
    ) -> ResponseUserProfileSchema:
        """Update profile of the user who made the request.

        Allows users to update their own profile information without
        additional permission checks.

        Args:
            current_user: Authenticated user making the request
            update_data: Partial profile data for update

        Returns:
            Updated user profile
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

        Args:
            user_id: Target user identifier to update
            current_user: Authenticated user making the request
            update_data: Partial profile data for update

        Returns:
            Updated user profile

        Raises:
            PermissionError: If current user lacks update
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

    async def set_password(
            self,
            current_user_id: int,
            schema: SetPasswordSchema
    ) -> ResponseUserProfileSchema:
        """Set user password.

        Sets a password for the user if no password has been set.
        For example, when logging in through an external provider.

        Args:
            current_user_id: ID authenticated user making the request
            schema: The new user password.

        Raises:
            PasswordAlreadySetError: If the password is already set.
        """
        current_user: UserProfile = await (
            self.repository.get_one_object_or_raise(
            object_id=current_user_id
            )
        )
        if current_user.hashed_password is not None:
            raise PasswordAlreadySetError(
                detail=("Cannot set password when it is already set. "
                        "You can only change the password.")
            )
        return await self._update_user_password(
            user_id=current_user_id, plain_password=schema.new_password
        )

    async def change_password(
            self,
            current_user_id: int,
            schema: ChangePasswordSchema
    ) -> ResponseUserProfileSchema:
        """Change user password.

        Args:
            current_user_id: ID authenticated user making the request
            schema: old and new user password
        Raises:
            PasswordVerifyError: If the current password is incorrect.
        """
        current_user: UserProfile = await (
            self.repository.get_one_object_or_raise(
            object_id=current_user_id
            )
        )
        if not verify_password(
            plain_password=schema.old_password,
            hashed_password=current_user.hashed_password
        ):
            raise PasswordVerifyError(
                detail="Current password is incorrect."
            )
        return await self._update_user_password(
            user_id=current_user_id, plain_password=schema.new_password
        )

    async def send_recovery_code_via_email(self, user_phone: str) -> str:
        """Initiate password recovery via email.

        Creates a password recovery session, generates a one-time numeric
        verification code, stores its hashed value in cache, and sends the
        code to the user's email address.

        If the user with the given phone number does not exist, a fake
        recovery session is still created and returned to prevent user
        enumeration attacks.

        Args:
            user_phone: Phone number provided by the user.

        Returns:
            Public recovery session identifier.

        Security notes:
            - The raw recovery code is never stored.
            - User existence is not disclosed to the client.
            - All sensitive mappings are kept server-side (cache).
        """
        recovery_id = uuid.uuid4().hex
        recovery_code = secrets.randbelow(900_000) + 100_000
        hashed_code = get_password_hash(password=str(recovery_code))

        user = await self.user_repo.get_by_phone(user_phone=user_phone)

        # Always create a recovery session to prevent user enumeration
        if user is not None:
            await self.cache_repo.set_recovery_session(
                recovery_id=recovery_id,
                user_id=user.id,
            )
            await self.cache_repo.set_recovery_password_code(
                recovery_id=recovery_id,
                hashed_recovery_code=hashed_code,
            )
            await self.email_service.send_password_recovery_email(
                recipient_email=user.email,
                recovery_code=recovery_code,
            )

        return recovery_id

    async def check_recovery_code(
            self, recovery_id: str, input_code: int
    ) -> str:
        """Verify recovery code and issue password reset token.

        Validates the user-provided recovery code against the hashed value
        stored in cache. On success, invalidates the recovery session and
        issues a one-time password reset token.

        Args:
            recovery_id: Public recovery session identifier.
            input_code: Numeric code entered by the user.

        Returns:
            One-time password reset token.

        Raises:
            PasswordVerifyError: If the code is invalid or expired.

        Security notes:
            - Recovery codes are single-use.
            - Session is destroyed immediately after successful verification.
            - Reset token has limited TTL and is also single-use.
        """
        hashed_code = await self.cache_repo.get_recovery_password_code(
            recovery_id=recovery_id
        )
        user_id = await self.cache_repo.get_recovery_session_user(
            recovery_id=recovery_id
        )

        if hashed_code is None or user_id is None:
            raise PasswordVerifyError(
                detail="Verification code is invalid or expired. "
                "Please try again."
            )

        if not verify_password(
                plain_password=str(input_code),
                hashed_password=hashed_code,
        ):
            raise PasswordVerifyError(
                detail="Verification code is invalid or expired. "
                "Please try again."
            )

        # Invalidate recovery session
        await self.cache_repo.delete_recovery_password_code(
            recovery_id=recovery_id
        )
        await self.cache_repo.delete_recovery_session(
            recovery_id=recovery_id
        )

        reset_token = uuid.uuid4().hex
        await self.cache_repo.set_recovery_token(
            reset_token=reset_token,
            user_id=user_id,
        )

        return reset_token

    async def reset_password_via_token(
            self, token: str, new_password: str
    ) -> ResponseUserProfileSchema:
        """Reset user password using a recovery token.

        Completes the password recovery flow by validating the provided
        reset token and setting a new password for the associated user.

        Args:
            token: One-time password reset token.
            new_password: New plain-text password.

        Returns:
            Updated user profile with sensitive fields excluded.

        Raises:
            InvalidResetToken: If the token is invalid or expired.

        Security notes:
            - Reset tokens are single-use.
            - Token is removed immediately after successful password reset.
            - Password is hashed before persistence.
        """
        user_id = await self.cache_repo.get_recovery_token(
            reset_token=token
        )
        if user_id is None:
            raise InvalidResetToken()

        await self.cache_repo.delete_recovery_token(
            reset_token=token
        )

        return await self._update_user_password(
            user_id=user_id,
            plain_password=new_password,
        )

    async def delete_user(
        self, user_id: int, current_user: UserProfile
    ) -> None:
        """Delete user with permission validation and media cleanup.

        Performs complete user deletion including: - Permission
        validation for deletion rights - Media file cleanup for user
        owned content - Database record deletion

        Args:
            user_id: Target user identifier to delete
            current_user: Authenticated user making the request

        Raises:
            PermissionError: If current user lacks deletion permissions
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

    async def _update_user_password(
            self, user_id: int, plain_password: str
    ) -> ResponseUserProfileSchema:
        """Update user's password with hashing.

        Internal helper method that hashes the provided plain-text password
        and persists it to the database.

        Args:
            user_id: Identifier of the user whose password is updated.
            plain_password: New plain-text password.

        Returns:
            Updated user profile serialized as response schema.

        Note:
            This method assumes all necessary validation has already been
            performed by the caller.
        """
        hashed_password = get_password_hash(password=plain_password)
        update_data = UpdatePasswordORMSchema(hashed_password=hashed_password)
        return await super().update_object(
            object_id=user_id, update_data=update_data
        )
