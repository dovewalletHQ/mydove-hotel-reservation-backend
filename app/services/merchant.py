"""Merchant Service - Business logic layer for merchant/owner operations"""

from datetime import datetime
from typing import Dict, List, Any

from app.core.logger import setup_logger
from app.repositories.hotel import HotelRepository
from app.repositories.booking import BookingRepository
from app.models.hotel import Hotel, HotelSuite
from app.models.booking import Booking, BookingStatus
from app.models.money import Money


logger = setup_logger(name="merchant_service")


class MerchantService:
    """Service for handling merchant/owner specific business logic"""

    @staticmethod
    async def get_merchant_hotels(owner_id: str) -> List[Hotel]:
        """Get all hotels owned by a merchant"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id: owner_id cannot be None or empty")

        logger.info("Getting hotels for merchant: %s", owner_id)
        return await HotelRepository.get_hotels_by_owner_id(owner_id)

    @staticmethod
    async def _verify_hotel_ownership(owner_id: str, hotel_id: str) -> Hotel:
        """Verify that a merchant owns a specific hotel"""
        hotel = await HotelRepository.get_hotel_by_id(hotel_id)
        if not hotel:
            raise ValueError("Hotel not found")

        if hotel.owner_id != owner_id:
            raise ValueError("Not authorized to access this hotel")

        return hotel

    @staticmethod
    async def update_hotel_details(
        owner_id: str,
        hotel_id: str,
        update_data: Dict[str, Any]
    ) -> Hotel:
        """Update hotel details - only the owner can update"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        logger.info("Merchant %s updating hotel %s", owner_id, hotel_id)
        return await HotelRepository.update_hotel(hotel_id, update_data)

    @staticmethod
    async def set_hotel_availability(
        owner_id: str,
        hotel_id: str,
        is_open: bool
    ) -> Hotel:
        """Set hotel availability (open/closed for the day)"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        logger.info("Merchant %s setting hotel %s availability to %s",
                   owner_id, hotel_id, is_open)
        return await HotelRepository.toggle_hotel_availability(hotel_id, is_open)

    @staticmethod
    async def get_merchant_hotel_suites(owner_id: str, hotel_id: str) -> List[HotelSuite]:
        """Get all suites for a merchant's hotel"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        logger.info("Getting suites for merchant %s hotel %s", owner_id, hotel_id)
        return await HotelRepository.get_hotel_suites_by_id(hotel_id)

    @staticmethod
    async def set_suite_availability(
        owner_id: str,
        hotel_id: str,
        suite_id: str,
        is_available: bool
    ) -> HotelSuite:
        """Set suite availability - only the hotel owner can change"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        # Get and update the suite
        suite = await HotelRepository.get_hotel_suite_by_id(suite_id)
        if not suite:
            raise ValueError("Suite not found")

        if suite.hotel_id != hotel_id:
            raise ValueError("Suite does not belong to this hotel")

        suite.is_available = is_available
        suite.updatedAt = datetime.now()
        await suite.save()

        logger.info("Merchant %s set suite %s availability to %s",
                   owner_id, suite_id, is_available)
        return suite

    @staticmethod
    async def get_merchant_bookings(owner_id: str) -> List[Booking]:
        """Get all bookings for all hotels owned by a merchant"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Get all hotels owned by the merchant
        hotels = await HotelRepository.get_hotels_by_owner_id(owner_id)

        all_bookings = []
        for hotel in hotels:
            bookings = await BookingRepository.get_bookings_by_hotel_id(str(hotel.id))
            all_bookings.extend(bookings)

        logger.info("Retrieved %d bookings for merchant %s", len(all_bookings), owner_id)
        return all_bookings

    @staticmethod
    async def get_merchant_bookings_by_hotel(
        owner_id: str,
        hotel_id: str
    ) -> List[Booking]:
        """Get all bookings for a specific hotel owned by the merchant"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        logger.info("Getting bookings for merchant %s hotel %s", owner_id, hotel_id)
        return await BookingRepository.get_bookings_by_hotel_id(hotel_id)

    @staticmethod
    async def get_merchant_revenue_summary(owner_id: str) -> Dict[str, Any]:
        """Get revenue summary for all merchant's hotels"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Get all hotels owned by the merchant
        hotels = await HotelRepository.get_hotels_by_owner_id(owner_id)

        total_bookings = 0
        completed_bookings = 0
        total_revenue = Money("0.00")
        pending_bookings = 0
        cancelled_bookings = 0

        for hotel in hotels:
            bookings = await BookingRepository.get_bookings_by_hotel_id(str(hotel.id))
            total_bookings += len(bookings)

            for booking in bookings:
                if booking.status == BookingStatus.COMPLETED:
                    completed_bookings += 1
                    total_revenue = Money(str(float(total_revenue) + float(booking.total_amount)))
                elif booking.status == BookingStatus.CHECKED_OUT:
                    completed_bookings += 1
                    total_revenue = Money(str(float(total_revenue) + float(booking.total_amount)))
                elif booking.status == BookingStatus.PENDING:
                    pending_bookings += 1
                elif booking.status == BookingStatus.CANCELLED:
                    cancelled_bookings += 1

        logger.info("Revenue summary for merchant %s: %s", owner_id, total_revenue)

        return {
            "total_hotels": len(hotels),
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "pending_bookings": pending_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": float(total_revenue)
        }

    @staticmethod
    async def get_hotel_dashboard_stats(owner_id: str, hotel_id: str) -> Dict[str, Any]:
        """Get dashboard statistics for a specific hotel"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        # Get suites
        suites = await HotelRepository.get_hotel_suites_by_id(hotel_id)
        available_suites = await HotelRepository.get_available_hotel_suites_by_hotel_id(hotel_id)
        unavailable_suites = await HotelRepository.get_unavailable_hotel_suites_by_hotel_id(hotel_id)

        # Get bookings
        bookings = await BookingRepository.get_bookings_by_hotel_id(hotel_id)

        pending_bookings = len([b for b in bookings if b.status == BookingStatus.PENDING])
        confirmed_bookings = len([b for b in bookings if b.status == BookingStatus.CONFIRMED])
        checked_in_guests = len([b for b in bookings if b.status == BookingStatus.CHECKED_IN])

        # Calculate today's revenue
        today = datetime.now().date()
        today_revenue = Money("0.00")
        for booking in bookings:
            if (booking.status in [BookingStatus.COMPLETED, BookingStatus.CHECKED_OUT] and
                booking.updatedAt.date() == today):
                today_revenue = Money(str(float(today_revenue) + float(booking.total_amount)))

        logger.info("Dashboard stats for hotel %s", hotel_id)

        return {
            "total_suites": len(suites),
            "available_suites": len(available_suites),
            "unavailable_suites": len(unavailable_suites),
            "total_bookings": len(bookings),
            "pending_bookings": pending_bookings,
            "confirmed_bookings": confirmed_bookings,
            "checked_in_guests": checked_in_guests,
            "today_revenue": float(today_revenue)
        }

    @staticmethod
    async def create_hotel(owner_id: str, hotel_data: Dict[str, Any]) -> Hotel:
        """Create a new hotel for a merchant"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        hotel = Hotel(
            owner_id=owner_id,
            name=hotel_data.get("name"),
            address=hotel_data.get("address"),
            email_address=hotel_data.get("email_address"),
            phone_number=hotel_data.get("phone_number"),
            state=hotel_data.get("state"),
            country=hotel_data.get("country"),
            lga=hotel_data.get("lga"),
            registration_type=hotel_data.get("registration_type", "CAC"),
            registration_image_link=hotel_data.get("registration_image_link"),
            is_approved=False,  # Hotels need admin approval
            is_open=True
        )

        logger.info("Creating hotel for merchant %s: %s", owner_id[:4], hotel.name)
        return await HotelRepository.create_hotel(hotel)

    @staticmethod
    async def create_suite(
        owner_id: str,
        hotel_id: str,
        suite_data: Dict[str, Any]
    ) -> HotelSuite:
        """Create a new suite for a merchant's hotel"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        suite = HotelSuite(
            hotel_id=hotel_id,
            name=suite_data.get("name"),
            price=suite_data.get("price"),
            description=suite_data.get("description"),
            room_number=suite_data.get("room_number"),
            room_type=suite_data.get("room_type"),
            facilities=suite_data.get("facilities", []),
            suite_photo_urls=suite_data.get("suite_photo_urls", []),
            is_available=suite_data.get("is_available", True)
        )

        logger.info("Creating suite for merchant %s hotel %s: %s",
                   owner_id, hotel_id, suite.name)
        return await HotelRepository.create_hotel_suite(suite)

    @staticmethod
    async def update_suite(
        owner_id: str,
        hotel_id: str,
        suite_id: str,
        update_data: Dict[str, Any]
    ) -> HotelSuite:
        """Update a suite in a merchant's hotel"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        suite = await HotelRepository.get_hotel_suite_by_id(suite_id)
        if not suite:
            raise ValueError("Suite not found")

        if suite.hotel_id != hotel_id:
            raise ValueError("Suite does not belong to this hotel")

        logger.info("Updating suite %s for merchant %s", suite_id, owner_id)
        return await HotelRepository.update_hotel_suite(suite_id, update_data)

    @staticmethod
    async def delete_suite(owner_id: str, hotel_id: str, suite_id: str) -> HotelSuite:
        """Delete a suite from a merchant's hotel"""
        if not owner_id or not str(owner_id).strip():
            raise ValueError("Invalid owner_id")

        # Verify ownership
        await MerchantService._verify_hotel_ownership(owner_id, hotel_id)

        suite = await HotelRepository.get_hotel_suite_by_id(suite_id)
        if not suite:
            raise ValueError("Suite not found")

        if suite.hotel_id != hotel_id:
            raise ValueError("Suite does not belong to this hotel")

        # Check if there are any active bookings for this suite
        bookings = await BookingRepository.get_bookings_by_suite_id(suite_id)
        active_bookings = [
            b for b in bookings
            if b.status in [BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.CHECKED_IN]
        ]

        if active_bookings:
            raise ValueError("Cannot delete suite with active bookings")

        logger.info("Deleting suite %s for merchant %s", suite_id, owner_id)
        return await HotelRepository.delete_hotel_suite(suite_id)

