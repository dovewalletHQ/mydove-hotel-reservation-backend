from pydantic import Field

from app.models.base import BaseMongoModel
from app.models.money import Money

class HotelSuite(BaseMongoModel):
    hotel_id: int
    name: str = Field(..., min_length=1)
    price: Money = Field(...,gt=0, alias="price")
    description: str = Field(..., min_length=1)
    room_number: int = Field(...,gt=0)
    facilities: list[str]
    is_available: bool = Field(default=True)

    class Setting:
        name = "hotel_suite"
