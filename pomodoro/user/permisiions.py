"""Проверки доступов."""

from pomodoro.core.exceptions.acces_denied import AccessDenied
from pomodoro.user.models.users import UserProfile, UserRole
from pomodoro.user.schemas.user import ResponseUserProfileSchema


async def check_update_permissions(
    target_user: ResponseUserProfileSchema, current_user: UserProfile
):
    """Проверяет, имеет ли текущий пользователь право обновлять target_user.

    Правила:
    - root может обновить кого угодно, включая себя, кроме других root.
    - admin может обновить себя, но не других админов или root.
    """
    # 1. Рут не может быть изменён никем, кроме себя
    if target_user.role == UserRole.ROOT and current_user.id != target_user.id:
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
