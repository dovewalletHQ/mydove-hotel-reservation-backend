"""Booking model for hotel reservations"""

import enum
from datetime import datetime
from typing import Optional

from pydantic import Field

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

