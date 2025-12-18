"""User repositories.

Provides data access layer for user entities with custom business logic.
Extends base CRUD repository with user-specific operations including
phone-based lookup and verification status management during updates.
"""

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from pomodoro.core.repositories.base_crud import CRUDRepository
from pomodoro.user.models.users import UserProfile


class UserRepository(CRUDRepository[UserProfile]):
    """User repository inheriting from base CRUD repository.

    Provides data access operations for UserProfile entities with
    extended functionality for phone-based lookup and verification
    status management.

    Attributes:     sessionmaker: Async session factory for database
    operations     orm_model: UserProfile model class for ORM operations
    """

    def __init__(self, sessionmaker: async_sessionmaker):
        """Initialize user repository with database session.

        Args:     sessionmaker: Async session factory for database
        connectivity
        """
        super().__init__(sessionmaker=sessionmaker, orm_model=UserProfile)

    async def get_by_phone(self, user_phone: str) -> UserProfile | None:
        """Find user by phone number.

        Args:
            user_phone: Phone number to search for

        Returns:
            UserProfile instance if found, None if no user with
            given phone exists

        Note:
            - Phone numbers are expected to be in normalized format
              for accurate matching
        """
        async with self.sessionmaker() as session:
            query = select(UserProfile).where(UserProfile.phone == user_phone)
            result = await session.execute(query)
            user = result.scalar_one_or_none()
            return user

    async def update_object(self, object_id, update_data: BaseModel):
        """Update user data with verification status management.

        Handles user profile updates with automatic verification status
        reset when sensitive contact information (phone, email) is
        modified.

        Args:     object_id: User identifier to update     update_data:
        Partial user data for update operation

        Returns:     Updated UserProfile instance

        Note:     Automatically resets phone_verified to False when
        phone is updated     Automatically resets email_verified to
        False when email is updated     This ensures security by
        requiring re-verification of changed contact methods
        """
        # Reset phone verification if phone number is being updated
        if "phone" in update_data.model_dump(exclude_unset=True):
            update_data.phone_verified = False

        # Reset email verification if email address is being updated
        if "email" in update_data.model_dump(exclude_unset=True):
            update_data.email_verified = False

        return await super().update_object(object_id, update_data)
