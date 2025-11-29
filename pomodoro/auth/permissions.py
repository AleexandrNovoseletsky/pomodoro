"""Authentication permissions.

Provides authorization logic utilities for role-based and ownership-
based access control. Contains reusable permission checking functions
for validating user privileges and resource ownership across the
application.
"""

from typing import Any

from pomodoro.user.models.users import UserProfile, UserRole


async def require_owner(resource: Any, current_user: UserProfile) -> bool:
    """Verify if current user is the owner of the specified resource.

    Checks resource ownership by comparing the resource's author
    identifier with the current user's identifier. Used for ownership-
    based access control.

    Args:     resource: The resource object being accessed (e.g., Task,
    Category, UserProfile)     current_user: The authenticated user
    making the request

    Returns:     True if current user is the resource owner, False
    otherwise

    Note:     Assumes the resource has an 'author_id' attribute
    representing ownership.     Resources without this attribute will
    raise AttributeError.
    """
    if resource.author_id == current_user.id:
        return True
    return False


async def require_role(
    current_user: UserProfile, allowed_roles: tuple[UserRole, ...]
) -> bool:
    """Verify if current user has one of the specified roles.

    Performs role-based access control by checking if the current user's
    role is included in the list of allowed roles for the operation.

    Args:     current_user: The authenticated user making the request
    allowed_roles: Tuple of user roles permitted for the operation
    Example: (UserRole.ROOT, UserRole.ADMIN)

    Returns:     True if current user has an allowed role, False
    otherwise

    Note:     Uses tuple for allowed_roles for performance and
    immutability.     Role checking follows hierarchical permission
    model.
    """
    if current_user.role in allowed_roles:
        return True
    return False
