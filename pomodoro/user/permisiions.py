"""Access permission checks.

Provides authorization logic for user operations with role-based access
control. Defines permission validation rules for user updates and
administrative operations following hierarchical role permissions.
"""

from pomodoro.core.exceptions.acces_denied import AccessDenied
from pomodoro.user.models.users import UserProfile, UserRole
from pomodoro.user.schemas.user import ResponseUserProfileSchema


async def check_update_permissions(
    target_user: ResponseUserProfileSchema, current_user: UserProfile
):
    """Check if current user has permission to update target user.

    Implements hierarchical role-based permission system for user
    updates: - ROOT users can update anyone except other ROOT users -
    ADMIN users can update themselves but not other ADMINS or ROOT users
    - USER role users can only update themselves

    Args:     target_user: User profile being targeted for update
    current_user: Authenticated user attempting the update

    Raises:     AccessDenied: If current user lacks permission to update
    target user

    Rules:     1. ROOT users cannot be updated by anyone except
    themselves     2. ADMIN users can only be updated by themselves or
    ROOT users     3. Regular users can only update their own profiles
    """
    # 1. ROOT users cannot be modified by anyone except themselves
    if target_user.role == UserRole.ROOT and current_user.id != target_user.id:
        raise AccessDenied("Root users can only be updated by themselves.")

    # 2. ADMIN users can only be updated by themselves or ROOT users
    if target_user.role == UserRole.ADMIN:
        if current_user.role not in (UserRole.ROOT, UserRole.ADMIN):
            raise AccessDenied("Insufficient privileges to update admin user.")
        if (
            current_user.id != target_user.id
            and current_user.role != UserRole.ROOT
        ):
            raise AccessDenied("Admin cannot update another admin.")
