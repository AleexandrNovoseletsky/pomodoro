from jose import jwt

from auth.security import get_password_hash, verify_password, create_access_token
from custom_exceptions import UserNotFoundError, PasswordVerifyError
from models import UserProfile
from repositories import UserRepository
from schemas import CreateUserSchema, ResponseUserSchema, LoginUserSchema
from schemas.user import CreateUserORM
from services.crud import CRUDService


class UserProfileService(CRUDService):
    def __init__(
        self,
        repository: UserRepository,
    ):
        super().__init__(repository=repository, response_schema=ResponseUserSchema)

    async def register_user(self, user_data: CreateUserSchema) -> UserProfile:
        hashed_password = get_password_hash(password=user_data.password)
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]

        new_user_data = CreateUserORM(**user_dict)
        new_user = await self.repository.create_object(data=new_user_data)
        return new_user

    async def login(self, login_data: LoginUserSchema) -> jwt:
        user_or_none = await self.repository.get_by_phone(user_phone=login_data.phone)
        if user_or_none is None:
            raise UserNotFoundError(phone=login_data.phone)

        verify = verify_password(
            plain_password=login_data.password,
            hashed_password=user_or_none.hashed_password,
        )
        if not verify:
            raise PasswordVerifyError
        access_token = create_access_token(
            data={"sub": str(user_or_none.id), "role": user_or_none.role}
        )
        response: dict = {"access_token": access_token}
        return response
