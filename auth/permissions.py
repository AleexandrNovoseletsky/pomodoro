from typing import Any, Callable

from fastapi import Depends, HTTPException, status


def require_roles(*allowed_roles: str) -> Callable:
    from dependencies.user import get_current_user
    async def checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user.get('role') not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Access denied: requires one of roles {allowed_roles}'
            )
        return current_user

    return checker


def require_owner(resource: Any, current_user: dict) -> bool:
    if not resource:
        raise HTTPException(status_code=404, detail='Resource not found')
    owner_id = getattr(resource, 'author_id', None)
    if owner_id != current_user.get('user_id'):
        raise HTTPException(
            status_code=403,
            detail='Access denied: not the owner of this resource'
        )
    return True
