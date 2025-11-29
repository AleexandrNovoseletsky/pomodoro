"""Yandex OAuth client implementation.

Provides integration with Yandex OAuth 2.0 for user authentication and
profile data retrieval. Handles token exchange and user information
fetching from Yandex ID API.
"""

import requests

from pomodoro.auth.schemas.yandex_user import YandexUserInfo
from pomodoro.core.settings import Settings

settings = Settings()


class YandexClient:
    """Yandex OAuth client for user authentication and data retrieval.

    Handles the complete OAuth 2.0 authorization flow including: - Token
    exchange using authorization codes - User profile data retrieval
    from Yandex ID API - Data validation and transformation
    """

    async def get_user_info(self, code: str) -> YandexUserInfo:
        """Retrieve user information from Yandex.

        Implements the OAuth 2.0 code exchange flow: 1. Exchange
        authorization code for access token 2. Use access token to fetch
        user profile data 3. Validate and return structured user
        information

        Args:     code: Authorization code received from Yandex OAuth
        redirect

        Returns:     Validated YandexUserInfo schema instance with user
        profile data

        Raises:     HTTPError: If Yandex API requests fail
        ValidationError: If Yandex response doesn't match expected
        schema

        Note:     Includes timeout protection for external API calls
        """
        access_token = self._get_user_access_token(code=code)
        user_info = requests.get(
            url="https://login.yandex.ru/info?format=json",
            headers={"Authorization": f"OAuth {access_token}"},
            timeout=5,
        )
        return YandexUserInfo(**user_info.json())

    @staticmethod
    def _get_user_access_token(code: str) -> str:
        """Exchange authorization code for access token.

        Performs the OAuth 2.0 token exchange with Yandex authorization
        server.

        Args:     code: Authorization code from Yandex OAuth flow

        Returns:     Access token string for API authentication

        Raises:     HTTPError: If token exchange request fails
        KeyError: If access token is not present in response

        Note:     Uses application/x-www-form-urlencoded content type as
        required     by Yandex OAuth specification
        """
        data = {
            "code": code,
            "client_id": settings.YANDEX_CLIENT_ID,
            "client_secret": settings.YANDEX_CLIENT_SECRET,
            "redirect_uri": settings.YANDEX_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        response = requests.post(
            url="https://oauth.yandex.ru/token",
            data=data,
            headers=headers,
            timeout=5,
        )
        return response.json()["access_token"]
