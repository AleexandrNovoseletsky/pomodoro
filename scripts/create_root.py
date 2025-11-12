from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth.security import get_password_hash
from app.core.settings import Settings
import app.task.models.tasks  # noqa: F401
import app.task.models.categories  # noqa: F401
from app.user.models.users import UserProfile
from app.user.schemas.user import CreateUserProfileORM, UserRole


BASE = "http://127.0.0.1:8000"
settings = Settings()


def create_root() -> None:
    engine = create_engine(settings.DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = CreateUserProfileORM(
        first_name=input("Введите имя root-пользователя: "),
        last_name=input("Введите фамилию root-пользователя: "),
        phone=input("Введите телефон root-пользователя: "),
        hashed_password=get_password_hash(
            input("Введите пароль root-пользователя: ")
        ),
        about=None,
        email=None,
    )
    orm_user = UserProfile(**user.model_dump())
    orm_user.role = UserRole.ROOT

    session.add(orm_user)
    session.commit()
    session.refresh(orm_user)
    print(f"Создан root-пользователь с ID {orm_user.id}")


if __name__ == "__main__":
    create_root()
