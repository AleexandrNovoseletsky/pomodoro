"""Authentication repositories.

Provides data access layer for authentication-related entities with
OAuth support. Extends base CRUD repository with OAuth-specific
operations for external identity management.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.auth.models.oauth_accaunts import OAuthAccount
from pomodoro.core.repositories.base_crud import CRUDRepository


class AuthRepository(CRUDRepository):
    """Authentication repository for OAuth account management.

    Extends base CRUD operations with OAuth-specific queries and
    operations for managing external authentication providers and user
    identities.

    Attributes:     sessionmaker: Async session factory for database
    operations     orm_model: OAuthAccount model class for ORM
    operations
    """

    def __init__(self, sessionmaker: async_sessionmaker):
        """Initialize authentication repository.

        Args:     sessionmaker: Async session factory for database
        connectivity
        """
        super().__init__(sessionmaker=sessionmaker, orm_model=OAuthAccount)

    async def get_by_provider_user(
        self, provider: str, provider_user_id: str
    ) -> OAuthAccount | None:
        """Retrieve OAuth account by provider.

        Searches for existing OAuth account linking to determine if a
        user has already connected their account with a specific OAuth
        provider.

        Args:     provider: OAuth provider name (e.g., 'yandex',
        'google')     provider_user_id: Unique user identifier from the
        OAuth provider

        Returns:     OAuthAccount instance if found, None if no account
        exists     for the given provider and user identifier

        Note:     This method is essential for OAuth login flow to
        handle both     new user registration and existing user
        authentication
        """
        async with self.sessionmaker() as session:
            query = (
                select(OAuthAccount)
                .where(OAuthAccount.provider == provider)
                .where(OAuthAccount.provider_user_id == provider_user_id)
            )
            result = await session.execute(query)
            return result.scalar_one_or_none()
