"""Authentication services.

Provides business logic layer for user authentication operations
including credential-based login and OAuth integration with external
providers. Handles user verification, token generation, and OAuth
account linking.
"""

from pomodoro.auth.clients.yandex import YandexClient
from pomodoro.auth.exceptions.password_incorrect import PasswordVerifyError
from pomodoro.auth.repositories.auth import AuthRepository
from pomodoro.auth.schemas.oauth import AccessTokenSchema, OAuthCreateORM
from pomodoro.auth.security import (
    create_access_token,
    verify_password,
)
from pomodoro.auth.services.mappers import yandex_to_user_and_oauth
from pomodoro.core.settings import Settings
from pomodoro.user.exceptions.user_not_found import UserNotFoundError
from pomodoro.user.models.users import UserProfile
from pomodoro.user.repositories.user import UserRepository
from pomodoro.user.schemas.user import UpdateUserProfileSchema

PROFILE_FIELDS_TO_ENRICH = (
    "first_name",
    "last_name",
    "birthday",
    "email",
)


class AuthService:
    """Authentication service for user login and OAuth integration.

    Handles both traditional credential-based authentication and OAuth
    flows with external providers like Yandex. Manages user
    verification, token generation, and OAuth account linking.

    Attributes:     settings: Application configuration settings
    client: Yandex OAuth client for external authentication
    user_repo: User repository for user data operations     auth_repo:
    Authentication repository for OAuth account management
    """

    def __init__(self, user_repo: UserRepository, auth_repo: AuthRepository):
        """Initialize authentication service with dependencies.

        Args:     user_repo: User repository for user profile operations
        auth_repo: Authentication repository for OAuth account
        management
        """
        self.settings = Settings()
        self.client = YandexClient()
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def login(self, phone: str, password: str) -> AccessTokenSchema:
        """Authenticate user with phone and password credentials.

        Performs user verification including existence check, active
        status validation, and password verification before issuing
        access token.

        Args:
            phone:
                User's phone number used as login identifier
            password:
                Plain text password for authentication

        Returns:
            AccessTokenSchema containing JWT token for API
            authorization

        Raises:
            UserNotFoundError:
                If no active user exists
                with the provided phone
            PasswordVerifyError:
                If provided password doesn't match
                stored hash
        """
        user_or_none = await self.user_repo.get_by_phone(user_phone=phone)
        if user_or_none.hashed_password is None:
            raise PasswordVerifyError(detail="Этот аккаунт создан через OAuth.")
        if user_or_none is None:
            raise UserNotFoundError(phone=phone)
        if not user_or_none.is_active:
            raise UserNotFoundError(phone=phone)

        verify = verify_password(
            plain_password=password,
            hashed_password=user_or_none.hashed_password,
        )
        if not verify:
            raise PasswordVerifyError()
        access_token = create_access_token(data={"sub": str(user_or_none.id)})
        response = AccessTokenSchema(access_token=access_token)
        return response

    async def get_yandex_redirect_url(self) -> str:
        """Generate Yandex OAuth authorization URL.

        Returns:
            Pre-configured redirect URL for Yandex OAuth
            authorization flow
        """
        return self.settings.get_yandex_redirect_url

    async def get_yandex_auth(self, code: str) -> AccessTokenSchema:
        """Process Yandex OAuth authentication flow.

        Handles complete Yandex OAuth flow including: - User data
        retrieval from Yandex API - OAuth account linking and user
        creation - Profile data enrichment for existing users - Access
        token generation

        Args:
            code: Authorization code received from Yandex OAuth
                  redirect

        Returns:
            AccessTokenSchema containing JWT token for API
            authorization
        """
        # Retrieve user profile data from Yandex OAuth API
        user_data = await self.client.get_user_info(code=code)

        # Transform Yandex data to application schemas
        user_schema, oauth_schema = yandex_to_user_and_oauth(data=user_data)

        # Check if OAuth account already exists
        oauth_user_or_none = await self.auth_repo.get_by_provider_user(
            provider=oauth_schema.provider,
            provider_user_id=oauth_schema.provider_user_id,
        )

        # Handle new OAuth user registration
        if oauth_user_or_none is None:
            user: UserProfile | None = None
            # Attempt to find existing user by phone number
            if user_schema.phone is not None:
                user = await self.user_repo.get_by_phone(
                    user_phone=user_schema.phone
                )

            # Create new user if not found
            if user is None:
                user = await self.user_repo.create_object(data=user_schema)
            else:
                # Enrich existing user profile with OAuth data
                update_data: dict = {}
                # Update empty fields with data from OAuth provider
                for field in PROFILE_FIELDS_TO_ENRICH:
                    provider_value = getattr(user_schema, field, None)
                    current_value = getattr(user, field, None)
                    # Only update if field is empty and provider has data
                    if current_value is None and provider_value not in (
                        None,
                        "",
                    ):
                        update_data[field] = provider_value

                if update_data:
                    await self.user_repo.update_object(
                        object_id=user.id,
                        update_data=UpdateUserProfileSchema(**update_data),
                    )

            # Create OAuth account linking
            create_data = OAuthCreateORM(
                **oauth_schema.model_dump(), user_id=user.id
            )
            await self.auth_repo.create_object(data=create_data)

        # Handle existing OAuth user login
        else:
            user = await self.user_repo.get_object(
                object_id=oauth_user_or_none.user_id
            )

        # Generate access token for authenticated user
        access_token = create_access_token(data={"sub": str(user.id)})
        response = AccessTokenSchema(access_token=access_token)
        return response
