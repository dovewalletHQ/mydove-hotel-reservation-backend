import enum
from pydantic import Field

from app.models.base import BaseMongoModel
from app.models.money import Money


class RoomType(str, enum.Enum):
    REGULAR = "Regular"
    STANDARD = "Standard"
    DELUXE = "Deluxe"
    SUITE = "Suite"
    VIP = "VIP"
    VVIP = "VVIP"
    PLATINUM = "Platinum"
    GOLD = "Gold"
    SILVER = "Silver"
    BRONZE = "Bronze"
    FAMILY = "Family"
    

class HotelSuite(BaseMongoModel):
    hotel_id: str
    name: str = Field(..., min_length=1)
    price: Money = Field(...,gt=0, alias="price")
    description: str = Field(..., min_length=1)
    room_number: int = Field(...,gt=0)
    room_type: RoomType = Field(default=RoomType.REGULAR, min_length=1)
    facilities: list[str]
    is_available: bool = Field(default=True)

    class Settings:
        name = "hotel_suite"


class Hotel(BaseMongoModel):
    """Data model for Hotel information."""
    owner_id: str
    name: str
    email_address: str
    phone_number: str
    state: str
    country: str
    lga: str
    registration_type: str = Field(default="CAC", description="Type of registration, default is CAC")
    registration_image_link: str = Field(default=None, description="Link to the cloudinary/image site handler document")
    is_approved: bool = False

    class Settings:
        name = "hotel"