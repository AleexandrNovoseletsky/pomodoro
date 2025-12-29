"""User management routes.

Provides REST API endpoints for user profile management and
administration. Includes routes for self-service operations and
administrative functions with proper role-based access control.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi_limiter.depends import RateLimiter

from pomodoro.auth.dependencies.auth import require_roles
from pomodoro.user.dependencies.user import get_current_user, get_user_service
from pomodoro.user.models.users import UserProfile, UserRole
from pomodoro.user.schemas.user import (
    ChangePasswordSchema,
    CheckRecoveryCodeSchema,
    ConfirmResetPasswordSchema,
    ResetPasswordSchema,
    ResponseUserProfileSchema,
    SetPasswordSchema,
    UpdateUserProfileSchema,
)
from pomodoro.user.services.user_service import UserProfileService

# Current authenticated user dependency
current_user_annotated = Annotated[
    UserProfile, Depends(dependency=get_current_user)
]

# User service dependency
user_service_annotated = Annotated[
    UserProfileService, Depends(dependency=get_user_service)
]

# Role constants for dependency configuration
admin = UserRole.ADMIN
root = UserRole.ROOT

router = APIRouter()


@router.get(
    path="/",
    response_model=list[ResponseUserProfileSchema],
    summary="Get all users",
    description=("Returns a list of all users in the system. "
                 "Administrator privileges required."),
)
async def get_users(
    user_service: user_service_annotated,
) -> list[ResponseUserProfileSchema]:
    """Get all users."""
    return await user_service.get_all_objects()


@router.get(
    path="/me",
    status_code=status.HTTP_200_OK,
    response_model=ResponseUserProfileSchema,
    summary="Get current user information",
    description=("Returns the profile of the user who made the request. "
                 "Available to all authenticated users."),
)
async def get_me(
    current_user: current_user_annotated,
) -> ResponseUserProfileSchema:
    """Get information about the user who made the request."""
    return ResponseUserProfileSchema.model_validate(current_user)


@router.patch(
    path="/me",
    status_code=status.HTTP_200_OK,
    response_model=ResponseUserProfileSchema,
    summary="Update current user data",
    description=("Update the profile of the user who made the request. "
                 "Available to all authenticated users."),
)
async def update_me(
    body: UpdateUserProfileSchema,
    current_user: current_user_annotated,
    user_service: user_service_annotated,
) -> ResponseUserProfileSchema:
    """Update data about the user who made the request."""
    return await user_service.update_me(
        current_user=current_user, update_data=body
    )


@router.patch(
    path="/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=ResponseUserProfileSchema,
    dependencies=[
        Depends(dependency=require_roles(allowed_roles=(root, admin))),
    ],
    summary="Update user data",
    description=("Update the profile of any user in the system. "
                 "Administrator or root privileges required."),
)
async def update_user(
    user_id: int,
    body: UpdateUserProfileSchema,
    current_user: current_user_annotated,
    user_service: user_service_annotated,
) -> ResponseUserProfileSchema:
    """Update user data.

    Available to administrators.
    """
    return await user_service.update_user(
        user_id=user_id, current_user=current_user, update_data=body
    )


@router.patch(
    path="/me/set_password",
    status_code=status.HTTP_200_OK,
    response_model=ResponseUserProfileSchema,
    summary="Set user password",
    description=("Sets a password for the user "
                 "if the password was not previously set. "
                 "For example, when logging in through an external provider.")
)
async def set_password(
        body: SetPasswordSchema,
        current_user: current_user_annotated,
        user_service: user_service_annotated
) -> ResponseUserProfileSchema:
    """Set the user's password.

    Available to current user only.
    """
    return await user_service.set_password(
        current_user_id=current_user.id, schema=body
    )


@router.patch(
    path="/me/change_password",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    response_model=ResponseUserProfileSchema,
    summary="Change user password",
    description="Replaces the user's current password with a new one."
)
async def change_password(
        body: ChangePasswordSchema,
        current_user: current_user_annotated,
        user_service: user_service_annotated
) -> ResponseUserProfileSchema:
    """Change the user's password.

    Available to current user only.
    """
    return await user_service.change_password(
        current_user_id=current_user.id, schema=body
    )


@router.post(
    path="/reset_password_via_email",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    summary="Password reset request via email",
    description="Sends a password reset code to the user's email."
)
async def reset_password_via_email(
        body: ResetPasswordSchema,
        user_service: user_service_annotated,
):
    """Send password recovery code via email.

    Args:
        body: Request body with user phone.
        user_service: User service dependency.

    Returns:
        Recovery session ID.
    """
    recovery_id = await user_service.send_recovery_code_via_email(
        user_phone=body.phone
    )
    return {
        "recovery_id": recovery_id,
    }


@router.post(
    path="/check_recovery_code",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    summary="Verify password recovery code",
    description=("Verifies the password recovery code. "
                "On success, redirects to the password reset page.")
)
async def check_recovery_code(
        body: CheckRecoveryCodeSchema,
        user_service: user_service_annotated
):
    """Check recovery code and return reset token.

    Args:
        body: Request body with recovery ID and code.
        user_service: User service dependency.

    Returns:
        Reset token for password change.
    """
    token = await user_service.check_recovery_code(
        recovery_id=body.recovery_id,
        input_code=body.recovery_code
    )
    return {
        "reset_token": token
    }


@router.patch(
    path="/confirm_reset_password",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RateLimiter(times=5, minutes=1))],
    response_model=ResponseUserProfileSchema,
    summary="Changes user password in exchange for token"
)
async def confirm_reset_password(
        body: ConfirmResetPasswordSchema,
        user_service: user_service_annotated
):
    """Reset user password using recovery token.

    Args:
        body: Request body with reset token and new password.
        user_service: User service dependency.

    Returns:
        Updated user profile.
    """
    return await user_service.reset_password_via_token(
        token=body.token, new_password=body.new_password
    )


@router.delete(
    path="/delete/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(dependency=require_roles(allowed_roles=(root,)))],
    summary="Delete user",
    description=("Complete removal of user from the system. "
                 "Root user privileges required.")
)
async def delete_user(
    user_id: int,
    user_service: user_service_annotated,
) -> None:
    """Delete user.

    Available to root only.
    """
    await user_service.delete_object(object_id=user_id)
