from app.auth.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.user.exceptions.user_not_found import UserNotFoundError
from app.auth.exceptions.password_incorrect import PasswordVerifyError
from app.user.repositories.user import UserRepository
from app.core.repositories.base_crud import HasId
from app.user.schemas.user import (
    CreateUserProfileSchema,
    LoginUserSchema,
    ResponseUserProfileSchema,
)
from app.user.schemas.user import CreateUserProfileORM
from app.core.services.base_crud import CRUDService


class UserProfileService(CRUDService):
    repository: UserRepository

    def __init__(
        self,
        user_repo: UserRepository,
    ):
        super().__init__(
            repository=user_repo, response_schema=ResponseUserProfileSchema
        )

    async def register_user(self, user_data: CreateUserProfileSchema) -> HasId:
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
        if user_or_none is None or user_or_none.is_active is False:
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
