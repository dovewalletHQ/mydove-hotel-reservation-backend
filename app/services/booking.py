"""Booking Service - Business logic layer for booking operations"""

from datetime import datetime
from typing import Dict, List, Any

from app.core.logger import setup_logger
from app.repositories.booking import BookingRepository
from app.repositories.hotel import HotelRepository
from app.models.booking import Booking, BookingType, BookingStatus


logger = setup_logger(name="booking_service")


class BookingService:
    """Service for handling booking business logic"""

    @staticmethod
    async def create_booking(booking_data: Dict[str, Any]) -> Booking:
        """
        Create a new booking.
        Validates hotel availability, suite availability, and date conflicts.
        """
        hotel_id = booking_data.get("hotel_id")
        suite_id = booking_data.get("suite_id")
        check_in_date = booking_data.get("check_in_date")
        check_out_date = booking_data.get("check_out_date")

        # Validate hotel exists
        hotel = await HotelRepository.get_hotel_by_id(hotel_id)
        if not hotel:
            raise ValueError("Hotel not found")

        # Check if hotel is open
        if not hotel.is_open:
            raise ValueError("Hotel is currently closed")

        # Validate suite exists and is available
        suite = await HotelRepository.get_hotel_suite_by_id(suite_id)
        if not suite:
            raise ValueError("Suite not found")

        if not suite.is_available:
            raise ValueError("Suite is not available")

        # Check for date conflicts
        is_available = await BookingRepository.check_suite_availability(
            suite_id,
            check_in_date,
            check_out_date
        )
        if not is_available:
            raise ValueError("Suite is not available for the selected dates")

        # Create the booking
        booking = Booking(
            hotel_id=hotel_id,
            suite_id=suite_id,
            guest_name=booking_data.get("guest_name"),
            guest_phone=booking_data.get("guest_phone"),
            guest_email=booking_data.get("guest_email"),
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            booking_type=booking_data.get("booking_type", BookingType.ONLINE),
            status=BookingStatus.PENDING,
            total_amount=booking_data.get("total_amount"),
            number_of_guests=booking_data.get("number_of_guests", 1),
            special_requests=booking_data.get("special_requests")
        )

        logger.info("Creating booking for guest: %s at hotel: %s",
                   booking.guest_name, hotel_id)

        return await BookingRepository.create_booking(booking)

    @staticmethod
    async def create_walk_in_booking(owner_id: str, booking_data: Dict[str, Any]) -> Booking:
        """
        Create a walk-in booking by a merchant/owner.
        Sets status to CHECKED_IN immediately.
        """
        hotel_id = booking_data.get("hotel_id")
        suite_id = booking_data.get("suite_id")
        check_in_date = booking_data.get("check_in_date")
        check_out_date = booking_data.get("check_out_date")

        # Validate hotel exists and owner matches
        hotel = await HotelRepository.get_hotel_by_id(hotel_id)
        if not hotel:
            raise ValueError("Hotel not found")

        if hotel.owner_id != owner_id:
            raise ValueError("Not authorized to create walk-in booking for this hotel")

        # Validate suite exists
        suite = await HotelRepository.get_hotel_suite_by_id(suite_id)
        if not suite:
            raise ValueError("Suite not found")

        if not suite.is_available:
            raise ValueError("Suite is not available")

        # Check for date conflicts
        is_available = await BookingRepository.check_suite_availability(
            suite_id,
            check_in_date,
            check_out_date
        )
        if not is_available:
            raise ValueError("Suite is not available for the selected dates")

        # Create walk-in booking with CHECKED_IN status
        booking = Booking(
            hotel_id=hotel_id,
            suite_id=suite_id,
            guest_name=booking_data.get("guest_name"),
            guest_phone=booking_data.get("guest_phone"),
            guest_email=booking_data.get("guest_email"),
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            booking_type=BookingType.WALK_IN,
            status=BookingStatus.CHECKED_IN,
            total_amount=booking_data.get("total_amount"),
            number_of_guests=booking_data.get("number_of_guests", 1),
            special_requests=booking_data.get("special_requests"),
            booked_by_owner_id=owner_id
        )

        logger.info("Creating walk-in booking by owner %s for guest: %s",
                   owner_id, booking.guest_name)

        return await BookingRepository.create_booking(booking)

    @staticmethod
    async def get_booking_details(booking_id: str) -> Booking:
        """Get detailed information about a booking"""
        if not booking_id or not booking_id.strip():
            raise ValueError("Invalid booking_id")

        booking = await BookingRepository.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        return booking

    @staticmethod
    async def cancel_booking(booking_id: str) -> Booking:
        """Cancel a booking"""
        if not booking_id or not booking_id.strip():
            raise ValueError("Invalid booking_id")

        booking = await BookingRepository.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        # Can't cancel already completed or checked-out bookings
        if booking.status in [BookingStatus.COMPLETED, BookingStatus.CHECKED_OUT]:
            raise ValueError("Cannot cancel a completed booking")

        logger.info("Cancelling booking: %s", booking_id)
        return await BookingRepository.update_booking_status(booking_id, BookingStatus.CANCELLED)

    @staticmethod
    async def confirm_booking(booking_id: str) -> Booking:
        """Confirm a pending booking"""
        if not booking_id or not booking_id.strip():
            raise ValueError("Invalid booking_id")

        booking = await BookingRepository.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        if booking.status != BookingStatus.PENDING:
            raise ValueError("Only pending bookings can be confirmed")

        logger.info("Confirming booking: %s", booking_id)
        return await BookingRepository.update_booking_status(booking_id, BookingStatus.CONFIRMED)

    @staticmethod
    async def check_in_guest(booking_id: str) -> Booking:
        """Check in a guest"""
        if not booking_id or not booking_id.strip():
            raise ValueError("Invalid booking_id")

        booking = await BookingRepository.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        if booking.status not in [BookingStatus.CONFIRMED, BookingStatus.PENDING]:
            raise ValueError("Booking must be confirmed before check-in")

        logger.info("Checking in guest for booking: %s", booking_id)
        return await BookingRepository.update_booking_status(booking_id, BookingStatus.CHECKED_IN)

    @staticmethod
    async def check_out_guest(booking_id: str) -> Booking:
        """Check out a guest"""
        if not booking_id or not booking_id.strip():
            raise ValueError("Invalid booking_id")

        booking = await BookingRepository.get_booking_by_id(booking_id)
        if not booking:
            raise ValueError("Booking not found")

        if booking.status != BookingStatus.CHECKED_IN:
            raise ValueError("Guest must be checked in before checkout")

        logger.info("Checking out guest for booking: %s", booking_id)
        return await BookingRepository.update_booking_status(booking_id, BookingStatus.CHECKED_OUT)

    @staticmethod
    async def get_booked_rooms_by_hotel(hotel_id: str) -> List[Booking]:
        """Get all current/active bookings for a hotel"""
        if not hotel_id or not hotel_id.strip():
            raise ValueError("Invalid hotel_id")

        # Get bookings that are not cancelled or completed
        all_bookings = await BookingRepository.get_bookings_by_hotel_id(hotel_id)

        active_statuses = [
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.CHECKED_IN
        ]

        return [b for b in all_bookings if b.status in active_statuses]

    @staticmethod
    async def get_bookings_for_merchant(owner_id: str) -> List[Booking]:
        """Get all bookings for hotels owned by a merchant"""
        if not owner_id or not owner_id.strip():
            raise ValueError("Invalid owner_id")

        # Get all hotels owned by the merchant
        hotels = await HotelRepository.get_hotels_by_owner_id(owner_id)

        all_bookings = []
        for hotel in hotels:
            bookings = await BookingRepository.get_bookings_by_hotel_id(str(hotel.id))
            all_bookings.extend(bookings)

        return all_bookings

    @staticmethod
    async def check_suite_availability_for_dates(
        suite_id: str,
        check_in: datetime,
        check_out: datetime
    ) -> bool:
        """Check if a suite is available for the given dates"""
        return await BookingRepository.check_suite_availability(suite_id, check_in, check_out)

