from datetime import date
from pydantic import BaseModel


class YandexPhone(BaseModel):
    id: int
    number: str


class YandexUserInfo(BaseModel):
    id: str
    first_name: str | None
    last_name: str | None
    access_token: str
    birthday: date | None = None
    default_phone: YandexPhone | None = None
    default_email: str
