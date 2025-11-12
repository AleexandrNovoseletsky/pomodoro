"""Маперы авторизации."""

from app.auth.schemas.oauth import OAuthCreateSchema
from app.auth.schemas.yandex_user import YandexUserInfo
from app.core.utils.normalize import normalize_name, normalize_phone
from app.user.schemas.user import CreateUserProfileSchema


def yandex_to_user_and_oauth(
    data: YandexUserInfo,
) -> tuple[CreateUserProfileSchema, OAuthCreateSchema]:
    """Преобразование данных полученных от Яндекса.

    В схему нашего пользователя,
    и схему пользователя от внешнего провайдера.
    """
    phone = None
    if data.default_phone is not None:
        phone = normalize_phone(data.default_phone.number)

    user = CreateUserProfileSchema(
        phone=phone,
        first_name=normalize_name(data.first_name),
        last_name=normalize_name(data.last_name),
        birthday=data.birthday,
        email=data.default_email,
        patronymic=None,
        about=None,
        password=None,
    )

    oauth = OAuthCreateSchema(
        provider="yandex",
        provider_user_id=data.id,
        phone=phone,
        first_name=normalize_name(data.first_name),
        last_name=normalize_name(data.last_name),
        birthday=data.birthday,
        email=data.default_email,
        access_token=data.access_token,
    )

    return user, oauth
