from app.auth.clients.yandex import YandexClient
from app.auth.models.oauth_accaunts import OAuthAccount
from app.auth.repositories.auth import AuthRepository
from app.auth.schemas.oauth import OAuthCreateORM
from app.auth.services.mappers import yandex_to_user_and_oauth
from app.core.settings import Settings
from app.user.models.users import UserProfile
from app.user.repositories.user import UserRepository
from app.user.schemas.user import UpdateUserSchema


class AuthService:
    def __init__(self, user_repo: UserRepository, auth_repo: AuthRepository):
        self.settings = Settings()
        self.client = YandexClient()
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def get_yandex_redirect_url(self) -> str:
        return self.settings.get_yandex_redirect_url

    async def get_yandex_auth(self, code: str) -> None:
        # Получаем данные пользователя из Яндекса
        user_data = await self.client.get_user_info(code=code)
        # Преобразуем полученные данные в схеу нашего пользователя
        # и в схему внешнего пользователя
        user_schema, oauth_schema = yandex_to_user_and_oauth(data=user_data)

        user: UserProfile | None = None
        oauth_user: OAuthAccount | None = None

        oauth_user = await self.auth_repo.get_by_provider_user(
            provider=oauth_schema.provider,
            provider_user_id=oauth_schema.provider_user_id
        )
        # Если внешнего пользователя ещё нет
        if oauth_user is None:
            # Если указан номер телефона
            if user_schema.phone is not None:
                # Ищем у нас пользователя по номеру телефона
                user = await self.user_repo.get_by_phone(
                    user_phone=user_schema.phone
                    )
            # если у нас пользователь не найден, или телефон не указан,
            # создаём нового пользователя.
            if user is None:
                user = await self.user_repo.create_object(
                    data=user_schema
                    )
            else:
                # Попытка одноразового обогащения профиля: заполняем
                # только отсутствующие поля (не перезаписываем существующие).
                update_data: dict = {}
                # Список полей, которые разумно подтянуть от провайдера
                for field in ("first_name", "last_name", "birthday", "email"):
                    provider_value = getattr(user_schema, field, None)
                    current_value = getattr(user, field, None)
                    if current_value in (None, "") and provider_value not in (
                        None,
                        "",
                    ):
                        update_data[field] = provider_value

                if update_data:
                    await self.user_repo.update_object(
                        object_id=user.id,
                        update_data=UpdateUserSchema(**update_data),
                    )
            create_data = OAuthCreateORM(
                **oauth_schema.model_dump(), user_id=user.id
                )
            oauth_user = await self.auth_repo.create_object(
                data=create_data
                )
        else:
            user = await self.user_repo.get_object(
                object_id=oauth_user.user_id
                )
