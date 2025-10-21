from fastapi.utils import BaseModel


class CreateCategorySchema(BaseModel):
    name: str

class ResponseCategorySchema(CreateCategorySchema):
    id: int

    class Config:
        from_attributes = True
