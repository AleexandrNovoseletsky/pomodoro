from app.auth.schemas.yandex_user import YandexUserInfo
from app.user.schemas.user import CreateUserProfileSchema
from app.auth.schemas.oauth import OAuthCreateSchema
from app.core.utils.normalize import normalize_phone, normalize_name


def yandex_to_user_and_oauth(
        data: YandexUserInfo
        ) -> tuple[CreateUserProfileSchema, OAuthCreateSchema]:
    phone = None
    if data.default_phone is not None:
        phone = normalize_phone(data.default_phone.number)

    user = CreateUserProfileSchema(
        phone=phone,
        first_name=normalize_name(data.first_name),
        last_name=normalize_name(data.last_name),
        birthday=data.birthday,
        email=data.default_email,
        about=None,
        password=None,
    )

    oauth = OAuthCreateSchema(
        provider='yandex',
        provider_user_id=data.id,
        phone=phone,
        first_name=normalize_name(data.first_name),
        last_name=normalize_name(data.last_name),
        birthday=data.birthday,
        email=data.default_email,
        access_token=data.access_token,
    )

    return user, oauth
