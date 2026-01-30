"""Booking model for hotel reservations"""

import enum
from datetime import datetime
from typing import Optional

from pydantic import Field, BaseModel

from app.models.base import BaseMongoModel
from app.models.money import Money


class BookingType(str, enum.Enum):
    """Type of booking - online or walk-in"""
    ONLINE = "online"
    WALK_IN = "walk_in"


class BookingStatus(str, enum.Enum):
    """Status of the booking"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    NO_SHOW = "no_show"


class Booking(BaseMongoModel):
    """Data model for hotel room bookings/reservations"""
    hotel_id: str = Field(..., description="ID of the hotel")
    suite_id: str = Field(..., description="ID of the hotel suite/room being booked")

    # Guest information
    guest_name: str = Field(..., min_length=1, description="Name of the guest")
    guest_phone: str = Field(..., min_length=1, description="Phone number of the guest")
    guest_email: Optional[str] = Field(default=None, description="Email of the guest (optional)")

    # Booking dates
    check_in_date: datetime = Field(..., description="Check-in date and time")
    check_out_date: datetime = Field(..., description="Check-out date and time")

    # Booking details
    booking_type: BookingType = Field(default=BookingType.ONLINE, description="Type of booking")
    status: BookingStatus = Field(default=BookingStatus.PENDING, description="Current status of the booking")
    total_amount: Money = Field(..., gt=0, description="Total amount for the booking")
    discount_amount: Money = Field(default=Money("0"), description="Discount amount applied to the booking")

    # For walk-in bookings, track which owner/merchant created it
    booked_by_owner_id: Optional[str] = Field(
        default=None,
        description="Owner ID who created this booking (for walk-in bookings)"
    )

    # Additional notes
    special_requests: Optional[str] = Field(default=None, description="Special requests from guest")
    number_of_guests: int = Field(default=1, ge=1, description="Number of guests")

    class Settings:
        name = "bookings"


class HotelSuiteBookingRequest(BaseModel):
    """Request model for booking a hotel suite"""
    hotel_id: str = Field(..., description="ID of the hotel")
    suite_id: str = Field(..., description="ID of the hotel suite/room being booked")
    guest_name: str = Field(..., min_length=1, description="Name of the guest")
    guest_phone: str = Field(..., min_length=1, description="Phone number of the guest")
    guest_email: Optional[str] = Field(default=None, description="Email of the guest (optional)")
    check_in_date: datetime = Field(..., description="Check-in date and time")
    check_out_date: datetime = Field(..., description="Check-out date and time")
    booking_type: BookingType = Field(default=BookingType.ONLINE, description="Type of booking")
    status: BookingStatus = Field(default=BookingStatus.PENDING, description="Current status of the booking")
    total_amount: Money = Field(..., gt=0, description="Total amount for the booking")
    discount_amount: Money = Field(default=Money("0"), description="Discount amount applied to the booking")
    booked_by_owner_id: Optional[str] = Field(
        default=None,
        description="Owner ID who created this booking (for walk-in bookings)"
    )
    special_requests: Optional[str] = Field(default=None, description="Special requests from guest")
    number_of_guests: int = Field(default=1, ge=1, description="Number of guests")


class HotelSuiteBookingResponse(BaseModel):
    """Response model for booking a hotel suite"""
    booking_id: str = Field(..., description="Unique identifier for this booking")
    hotel_id: str = Field(..., description="Hotel ID")
    suite_id: str = Field(..., description="Suite/room ID")
    suite_room_number: int = Field(..., description="Suite/room number")
    guest_name: str = Field(..., description="Name of the guest")
    guest_phone: str = Field(..., description="Guest phone number")
    guest_email: Optional[str] = Field(default=None, description="Guest email (if provided)")
    check_in_date: datetime = Field(..., description="Check-in datetime in ISO format")
    check_out_date: datetime = Field(..., description="Check-out datetime in ISO format")
    booking_type: BookingType = Field(default=BookingType.ONLINE, description="Booking type")
    status: BookingStatus = Field(default=BookingStatus.CONFIRMED, description="Booking status updated to confirmed")
    total_amount: Money = Field(..., gt=0, description="Total booking amount")
    discount_amount: Money = Field(default=Money("0"), description="Discount applied")
    final_amount: Money = Field(..., gt=0, description="Total minus discount")
    number_of_guests: int = Field(default=1, ge=1, description="Number of guests")
    special_requests: Optional[str] = Field(default=None, description="Any guest requests")
    booked_by_owner_id: Optional[str] = Field(default=None, description="Owner ID if a walk-in booking")
    confirmation_date: Optional[None | datetime] = Field(default=None, description="Timestamp when booking was confirmed")

class UserBookings(BaseModel):
    """Model representing a user's bookings"""
    guest_phone: str = Field(..., description="Phone number of the guest")