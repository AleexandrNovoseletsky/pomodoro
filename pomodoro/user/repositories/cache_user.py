"""User cache repository.

Handles temporary data for password recovery flows using Redis.
"""

from redis.asyncio import Redis

from pomodoro.core.settings import Settings

settings = Settings()


class UserCacheRepository:
    """Repository for user-related cache operations.

    Responsible for password recovery sessions, verification codes,
    and reset tokens.
    """

    def __init__(self, cache_session: Redis) -> None:
        """Initialize repository with Redis cache session.

        Args:
            cache_session: Authenticated Redis client.
        """
        self.cache_session = cache_session

    # Recovery session (recovery_id -> user_id)

    async def set_recovery_session(
        self, recovery_id: str, user_id: int
    ) -> None:
        """Bind recovery session to user.

        Args:
            recovery_id: Public recovery session identifier.
            user_id: Internal user identifier.
        """
        await self.cache_session.set(
            name=f"password_reset:session:{recovery_id}",
            value=str(user_id),
            ex=settings.RECOVERY_PASSWORD_CODE_LIFESPAN,
        )

    async def get_recovery_session_user(self, recovery_id: str) -> int | None:
        """Get user ID associated with recovery session.

        Args:
            recovery_id: Public recovery session identifier.

        Returns:
            User ID if session exists, otherwise None.
        """
        value = await self.cache_session.get(
            name=f"password_reset:session:{recovery_id}"
        )
        return int(value) if value is not None else None

    async def delete_recovery_session(self, recovery_id: str) -> None:
        """Delete recovery session mapping.

        Args:
            recovery_id: Public recovery session identifier.
        """
        await self.cache_session.delete(
            f"password_reset:session:{recovery_id}"
        )

    # Recovery verification code

    async def set_recovery_password_code(
        self, recovery_id: str, hashed_recovery_code: str
    ) -> None:
        """Store hashed recovery code.

        Args:
            recovery_id: Public recovery session identifier.
            hashed_recovery_code: Hashed numeric recovery code.
        """
        await self.cache_session.set(
            name=f"password_reset:code:{recovery_id}",
            value=hashed_recovery_code,
            ex=settings.RECOVERY_PASSWORD_CODE_LIFESPAN,
        )

    async def get_recovery_password_code(
        self, recovery_id: str
    ) -> str | None:
        """Retrieve hashed recovery code.

        Args:
            recovery_id: Public recovery session identifier.

        Returns:
            Hashed recovery code or None if expired.
        """
        return await self.cache_session.get(
            name=f"password_reset:code:{recovery_id}"
        )

    async def delete_recovery_password_code(self, recovery_id: str) -> None:
        """Delete recovery code.

        Args:
            recovery_id: Public recovery session identifier.
        """
        await self.cache_session.delete(
            f"password_reset:code:{recovery_id}"
        )

    # Password reset token

    async def set_recovery_token(
        self, reset_token: str, user_id: int
    ) -> None:
        """Store password reset token.

        Args:
            reset_token: One-time password reset token.
            user_id: Internal user identifier.
        """
        await self.cache_session.set(
            name=f"password_reset:token:{reset_token}",
            value=str(user_id),
            ex=settings.RECOVERY_PASSWORD_CODE_LIFESPAN,
        )

    async def get_recovery_token(self, reset_token: str) -> int | None:
        """Resolve reset token to user ID.

        Args:
            reset_token: One-time password reset token.

        Returns:
            User ID if token exists, otherwise None.
        """
        value = await self.cache_session.get(
            name=f"password_reset:token:{reset_token}"
        )
        return int(value) if value is not None else None

    async def delete_recovery_token(self, reset_token: str) -> None:
        """Delete password reset token.

        Args:
            reset_token: One-time password reset token.
        """
        await self.cache_session.delete(
            f"password_reset:token:{reset_token}"
        )
