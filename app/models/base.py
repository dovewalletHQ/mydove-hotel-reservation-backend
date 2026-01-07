# app/models/base.py
import logging
from datetime import datetime

from beanie import Document
from bson import ObjectId as BsonObjectId
from pydantic import Field, ConfigDict
from pydantic_core import core_schema

logger = logging.getLogger(__name__)


class PyObjectId(BsonObjectId):
    """Custom Pydantic-compatible ObjectId class for MongoDB _id fields."""

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        def validate(value):
            if not BsonObjectId.is_valid(value):
                raise ValueError("Invalid ObjectId")
            return BsonObjectId(value)

        return core_schema.no_info_plain_validator_function(
            function=validate,
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, _core_schema, handler):
        return handler(core_schema.str_schema())


class BaseMongoModel(Document):
    """Base model for MongoDB documents using Beanie, with custom ObjectId handling."""

    id: PyObjectId = Field(default_factory=BsonObjectId, alias="_id")
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Settings:
        bson_encoders = {BsonObjectId: str}  # Serialize ObjectId as string in JSON
        validate_on_save = True  # Validate data before saving to MongoDB

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure updatedAt is refreshed on instantiation if not provided
        if "updatedAt" not in kwargs:
            self.updatedAt = datetime.now()
