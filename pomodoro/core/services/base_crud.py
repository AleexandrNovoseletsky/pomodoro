"""Base class for all services.

CRUD operations.
"""
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from pomodoro.core.exceptions.integrity import IntegrityDBError
from pomodoro.core.exceptions.object_not_found import ObjectNotFoundError
from pomodoro.core.repositories.base_crud import CRUDRepository

ResponseSchema = TypeVar("ResponseSchema", bound=BaseModel)


class CRUDService(
    Generic[ResponseSchema]
):
    """Base service class providing CRUD operations.

    Serves as the foundation for all domain-specific services, handling
    data transformation between ORM objects and Pydantic schemas with
    consistent error handling and business logic encapsulation.

    Attributes:     repository: CRUD repository instance for data access
    operations     response_schema: Pydantic model class for response
    data serialization
    """

    def __init__(
        self, repository: CRUDRepository, response_schema: type[ResponseSchema]
    ):
        """Initialize base service with repository and response schema.

        Args:     repository: Domain-specific repository for data
        operations     response_schema: Pydantic model class for
        response serialization
        """
        self.repository = repository
        self.response_schema = response_schema

    async def get_one_object(self, object_id: int) -> ResponseSchema:
        """Retrieve a single object by identifier with validation.

        Args:     object_id: Unique identifier of the object to retrieve

        Returns:     Validated Pydantic response schema instance

        Raises:     ObjectNotFoundError: If no object exists with the
        specified ID

        Note:     Automatically converts ORM objects to Pydantic schemas
        for consistent API response formatting
        """
        db_object = await self.repository.get_object(object_id=object_id)
        if db_object is None:
            raise ObjectNotFoundError(object_id=object_id)
        return self.response_schema.model_validate(obj=db_object)

    async def get_all_objects(self) -> list[ResponseSchema]:
        """Retrieve all objects with schema validation.

        Returns:
            List of validated Pydantic response schema
            instances

        Note:
            Returns empty list if no objects exist in the
            repository
        """
        db_objects = await self.repository.get_all_objects()
        object_schema = [
            self.response_schema.model_validate(row) for row in db_objects
        ]
        return object_schema

    async def create_object(self, object_data: BaseModel) -> ResponseSchema:
        """Create a new object with data validation.

        Args:     object_data: Pydantic schema containing creation data

        Returns:     Validated Pydantic response schema of the created
        object

        Raises:     IntegrityDBError: If database constraints are
        violated     during object creation
        """
        try:
            new_object = await self.repository.create_object(data=object_data)
        except IntegrityError as e:
            raise IntegrityDBError(exc=e) from e
        return self.response_schema.model_validate(obj=new_object)

    async def update_object(
        self, object_id: int, update_data: BaseModel
    ) -> ResponseSchema:
        """Update an existing object with partial data and validation.

        Args:     object_id: Unique identifier of the object to update
        update_data: Pydantic schema containing update data

        Returns:     Validated Pydantic response schema of the updated
        object

        Raises:     IntegrityDBError: If database constraints are
        violated     ObjectNotFoundError: If no object exists with the
        specified ID
        """
        try:
            updated_object_or_none = await self.repository.update_object(
                object_id=object_id, update_data=update_data
            )
        except IntegrityError as e:
            raise IntegrityDBError(exc=e) from e
        if updated_object_or_none is None:
            raise ObjectNotFoundError(object_id=object_id)
        return self.response_schema.model_validate(obj=updated_object_or_none)

    async def delete_object(self, object_id: int) -> None:
        """Delete an object by identifier with existence validation.

        Args:     object_id: Unique identifier of the object to delete

        Raises:     ObjectNotFoundError: If no object exists with the
        specified ID

        Note:     Returns None on successful deletion to indicate
        operation completion     without returning data for deleted
        resources
        """
        deleted = await self.repository.delete_object(object_id=object_id)
        if not deleted:
            raise ObjectNotFoundError(object_id=object_id)
        return None
