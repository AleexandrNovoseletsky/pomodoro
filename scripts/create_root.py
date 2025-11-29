"""Root user creation script.

Creates initial root user with administrative privileges for system
bootstrap. Used for initial setup and administrative access
configuration.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pomodoro.task.models.categories
import pomodoro.task.models.tasks  # noqa: F401
from pomodoro.auth.security import get_password_hash
from pomodoro.core.settings import Settings
from pomodoro.user.models.users import UserProfile
from pomodoro.user.schemas.user import CreateUserProfileORM, UserRole

BASE = "http://127.0.0.1:8000"
settings = Settings()


def create_root() -> None:
    """Create root user with administrative privileges.

    Interactive script that prompts for root user details and creates a
    superuser account with ROOT role for system administration.

    Process: 1. Establishes database connection 2. Prompts for user
    details (name, phone, password) 3. Hashes password securely 4.
    Creates user with ROOT role 5. Commits to database and confirms
    creation

    Note:     This script should be run once during initial system
    setup.     Root users have full system access and should be created
    carefully.
    """
    engine = create_engine(settings.DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Collect user input for root user creation
    user = CreateUserProfileORM(
        first_name=input("Enter root user first name: "),
        last_name=input("Enter root user last name: "),
        phone=input("Enter root user phone number: "),
        hashed_password=get_password_hash(input("Enter root user password: ")),
        patronymic=None,
        about=None,
        email=None,
    )

    # Create ORM user with ROOT role
    orm_user = UserProfile(**user.model_dump())
    orm_user.role = UserRole.ROOT

    # Persist user to database
    session.add(orm_user)
    session.commit()
    session.refresh(orm_user)
    print(f"Created root user with ID {orm_user.id}")


if __name__ == "__main__":
    create_root()
