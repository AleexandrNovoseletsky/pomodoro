"""Сервисы авторизации."""

from app.auth.clients.yandex import YandexClient
from app.auth.exceptions.password_incorrect import PasswordVerifyError
from app.auth.models.oauth_accaunts import OAuthAccount
from app.auth.repositories.auth import AuthRepository
from app.auth.schemas.oauth import OAuthCreateORM
from app.auth.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.auth.services.mappers import yandex_to_user_and_oauth
from app.core.settings import Settings
from app.user.exceptions.user_not_found import UserNotFoundError
from app.user.models.users import UserProfile
from app.user.repositories.user import UserRepository
from app.user.schemas.user import (
    CreateUserProfileORM,
    CreateUserProfileSchema,
    ResponseUserProfileSchema,
    UpdateUserProfileSchema,
)


class AuthService:
    """Сервис аторизации."""

    def __init__(self, user_repo: UserRepository, auth_repo: AuthRepository):
        """Иннициализация сервиса."""
        self.settings = Settings()
        self.client = YandexClient()
        self.user_repo = user_repo
        self.auth_repo = auth_repo

    async def register_user(
        self, user_data: CreateUserProfileSchema
    ) -> ResponseUserProfileSchema:
        """Регистрация пользователя."""
        hashed_password = get_password_hash(password=user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]

        new_user_data = CreateUserProfileORM(**user_dict)
        new_user = await self.user_repo.create_object(data=new_user_data)
        return new_user

    async def login(self, phone: str, password: str) -> dict[str, str]:
        """Вход пользователя. Возвращает токен."""
        user_or_none = await self.user_repo.get_by_phone(
            user_phone=phone
        )
        if user_or_none is None or user_or_none.is_active is False:
            raise UserNotFoundError(phone=phone)

        verify = verify_password(
            plain_password=password,
            hashed_password=user_or_none.hashed_password,
        )
        if not verify:
            raise PasswordVerifyError
        access_token = create_access_token(data={"sub": str(user_or_none.id)})
        response = {"access_token": access_token}
        return response

    async def get_yandex_redirect_url(self) -> str:
        """Получение ссылки для авторизации через Яндекс."""
        return self.settings.get_yandex_redirect_url

    async def get_yandex_auth(self, code: str) -> dict[str, str]:
        """Получение авторизации от Яндекса. Возвращает наш токен."""
        # Получаем данные пользователя из Яндекса
        user_data = await self.client.get_user_info(code=code)
        # Преобразуем полученные данные в схему нашего пользователя
        # и в схему внешнего пользователя
        user_schema, oauth_schema = yandex_to_user_and_oauth(data=user_data)

        user: UserProfile | None = None
        oauth_user: OAuthAccount | None = None

        oauth_user = await self.auth_repo.get_by_provider_user(
            provider=oauth_schema.provider,
            provider_user_id=oauth_schema.provider_user_id,
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
                user = await self.user_repo.create_object(data=user_schema)
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
                        update_data=UpdateUserProfileSchema(**update_data),
                    )
            create_data = OAuthCreateORM(
                **oauth_schema.model_dump(), user_id=user.id
            )
            oauth_user = await self.auth_repo.create_object(data=create_data)
        else:
            user = await self.user_repo.get_object(
                object_id=oauth_user.user_id
            )
            if user is None:
                raise UserNotFoundError()

        access_token = create_access_token(data={"sub": str(user.id)})
        response = {"access_token": access_token}
        return response
