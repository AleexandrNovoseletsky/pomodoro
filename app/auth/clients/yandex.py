"""Клиенты авторизации через Яндекс."""

import requests

from app.auth.schemas.yandex_user import YandexUserInfo
from app.core.settings import Settings

settings = Settings()


class YandexClient:
    """Клиент авторизации через Яндекс."""

    async def get_user_info(self, code: str):
        """Получение данных о пользователе от Янжекса."""
        access_token = self._get_user_access_token(code=code)
        user_info = requests.get(
            url="https://login.yandex.ru/info?format=json",
            headers={"Authorization": f"OAuth {access_token}"},
            timeout=5,
        )
        return YandexUserInfo(**user_info.json(), access_token=access_token)

    def _get_user_access_token(self, code: str) -> str:
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
