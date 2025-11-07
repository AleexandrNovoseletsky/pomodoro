from auth import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from custom_exceptions import UserNotFoundError, PasswordVerifyError
from models import UserProfile
from repositories import UserRepository
from schemas import (
    CreateUserProfileSchema,
    LoginUserSchema,
)
from schemas.user import CreateUserProfileORM
from services.base_crud import CRUDService


class UserProfileService(CRUDService):
    def __init__(
        self,
        repository: UserRepository,
    ):
        super().__init__(repository=repository)

    async def register_user(
        self, user_data: CreateUserProfileSchema
    ) -> UserProfile:
        hashed_password = get_password_hash(password=user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]

        new_user_data = CreateUserProfileORM(**user_dict)
        new_user = await self.repository.create_object(data=new_user_data)
        return new_user

    async def login(self, login_data: LoginUserSchema) -> dict:
        user_or_none = await self.repository.get_by_phone(
            user_phone=login_data.phone
        )
        if user_or_none is None:
            raise UserNotFoundError(phone=login_data.phone)

        verify = verify_password(
            plain_password=login_data.password,
            hashed_password=user_or_none.hashed_password,
        )
        if not verify:
            raise PasswordVerifyError
        access_token = create_access_token(data={"sub": str(user_or_none.id)})
        response: dict = {"access_token": access_token}
        return response
