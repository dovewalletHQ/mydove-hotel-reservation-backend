import enum
from typing import List

from pydantic import Field, BaseModel

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
    facilities: List[str] = Field(default=[], description="List of facilities available in the room [optional]")
    suite_photo_urls: List[str] = Field(default=[], description="List of photo URLs for the suite [optional]")
    is_available: bool = Field(default=True)

    class Settings:
        name = "hotel_suite"

class HotelProfile(BaseMongoModel):
    """Data model for Hotel creation request."""
    hotel_id: str
    description: str | None = Field(default=None, description="Description of the hotel [optional]")
    website_url: str | None = Field(default=None, description="Website URL of the hotel [optional]")
    display_photo_url: List[str] | None = Field(default=None, description="List of display photo URLs for the hotel [optional]")
    instagram_handle: str | None = Field(default=None, description="Instagram handle of the hotel [optional]")
    facebook_handle: str | None = Field(default=None, description="Facebook handle of the hotel [optional]")
    twitter_handle: str | None = Field(default=None, description="Twitter handle of the hotel [optional]")

    class Settings:
        name = "hotel_profiles"


class Hotel(BaseMongoModel):
    """Data model for Hotel information."""
    owner_id: str
    name: str
    address: str | None = Field(default=None, description="Physical address of the hotel [optional]")
    email_address: str
    phone_number: str
    state: str
    country: str
    lga: str
    registration_type: str = Field(default="CAC", description="Type of registration, default is CAC")
    registration_image_link: str = Field(default=None, description="Link to the cloudinary/image site handler document")
    is_approved: bool = False
    is_open: bool = Field(default=True, description="Whether the hotel is open for business today")

    class Settings:
        name = "hotel"


class HotelResponse(BaseModel):
    """Data model for Hotel response with profile."""
    owner_id: str
    name: str
    address: str | None = Field(default=None, description="Physical address of the hotel [optional]")
    email_address: str
    phone_number: str
    state: str
    country: str
    lga: str
    is_open: bool = Field(default=True, description="Whether the hotel is open for business today")