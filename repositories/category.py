from sqlalchemy.orm import Session

from models import Categories
from repositories.crud import CRUDRepository


class CategoryRepository(CRUDRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session, Categories)
