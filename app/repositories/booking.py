"""Booking Repository - Data access layer for booking operations"""

from datetime import datetime
from typing import List, Optional

from beanie.odm.operators.find.comparison import NotIn

from app.core.logger import logger
from app.models.booking import Booking, BookingStatus


class BookingRepository:
    """Repository for booking/reservation database operations"""

    @staticmethod
    async def create_booking(booking: Booking) -> Booking:
        """Create a new booking"""
        logger.info("Creating booking for guest: %s", booking.guest_name)
        return await booking.save()

    @staticmethod
    async def get_booking_by_id(booking_id: str) -> Optional[Booking]:
        """Get a booking by its ID"""
        logger.info("Getting booking by id: %s", booking_id)
        try:
            return await Booking.get(booking_id)
        except Exception as e:
            logger.error("Failed to get booking by id: %s", e)
            return None
    
    @staticmethod
    async def get_booking_by_suite_id(suite_id: str) -> Optional[Booking]:
        """Get a booking by its suite_id"""
        logger.info("Getting booking by suite_id: %s", suite_id)
        try:
            return await Booking.find_one(Booking.suite_id == suite_id)
        except Exception as e:
            logger.error("Failed to get booking by suite_id: %s", e)
            return None

    @staticmethod
    async def get_bookings_by_hotel_id(hotel_id: str) -> List[Booking]:
        """Get all bookings for a specific hotel"""
        if not hotel_id or not hotel_id.strip():
            raise ValueError("Invalid hotel_id: hotel_id cannot be None or empty")

        logger.info("Getting bookings for hotel: %s", hotel_id)
        try:
            return await Booking.find(Booking.hotel_id == hotel_id).to_list()
        except Exception as e:
            logger.error("Failed to get bookings by hotel id: %s", e)
            raise

    @staticmethod
    async def get_bookings_by_guest_phone(guest_phone: str) -> List[Booking]:
        """Get all bookings for a specific guest phone number"""
        if not guest_phone or not guest_phone.strip():
            raise ValueError("Invalid guest_phone: guest_phone cannot be None or empty")

        logger.info("Getting bookings for guest phone: %s", guest_phone)
        try:
            return await Booking.find(Booking.guest_phone == guest_phone).to_list()
        except Exception as e:
            logger.error("Failed to get bookings by guest phone: %s", e)
            raise ValueError("Error retrieving bookings for guest")

    @staticmethod
    async def get_bookings_by_suite_id(suite_id: str) -> List[Booking]:
        """Get all bookings for a specific suite"""
        if not suite_id or not suite_id.strip():
            raise ValueError("Invalid suite_id: suite_id cannot be None or empty")

        logger.info("Getting bookings for suite: %s", suite_id)
        try:
            return await Booking.find(Booking.suite_id == suite_id).to_list()
        except Exception as e:
            logger.error("Failed to get bookings by suite id: %s", e)
            raise

    @staticmethod
    async def get_bookings_by_owner_id(owner_id: str) -> List[Booking]:
        """Get all bookings created by a specific owner (for walk-in bookings)"""
        if not owner_id or not owner_id.strip():
            raise ValueError("Invalid owner_id: owner_id cannot be None or empty")

        logger.info("Getting bookings by owner: %s", owner_id)
        try:
            return await Booking.find(Booking.booked_by_owner_id == owner_id).to_list()
        except Exception as e:
            logger.error("Failed to get bookings by owner id: %s", e)
            raise

    @staticmethod
    async def update_booking_status(booking_id: str, status: BookingStatus) -> Booking:
        """Update the status of a booking"""
        logger.info("Updating booking status: %s to %s", booking_id, status)
        try:
            booking = await Booking.get(booking_id)
            if not booking:
                raise ValueError("Booking not found")

            booking.status = status
            booking.updatedAt = datetime.now()
            await booking.save()
            return booking
        except ValueError:
            raise
        except Exception as e:
            logger.error("Failed to update booking status: %s", e)
            raise

    @staticmethod
    async def get_bookings_by_date_range(
        start_date: datetime,
        end_date: datetime,
        hotel_id: Optional[str] = None
    ) -> List[Booking]:
        """Get bookings within a date range, optionally filtered by hotel"""
        logger.info("Getting bookings from %s to %s", start_date, end_date)
        try:
            query = Booking.find(
                Booking.check_in_date >= start_date,
                Booking.check_out_date <= end_date
            )

            if hotel_id:
                query = Booking.find(
                    Booking.check_in_date >= start_date,
                    Booking.check_out_date <= end_date,
                    Booking.hotel_id == hotel_id
                )

            return await query.to_list()
        except Exception as e:
            logger.error("Failed to get bookings by date range: %s", e)
            raise

    @staticmethod
    async def delete_booking(booking_id: str) -> Booking:
        """Delete a booking by its ID"""
        logger.info("Deleting booking: %s", booking_id)
        try:
            booking = await Booking.get(booking_id)
            if not booking:
                raise ValueError("Booking not found")

            await booking.delete()
            return booking
        except ValueError:
            raise
        except Exception as e:
            logger.error("Failed to delete booking: %s", e)
            raise

    @staticmethod
    async def get_bookings_by_status(hotel_id: str, status: BookingStatus) -> List[Booking]:
        """Get bookings for a hotel filtered by status"""
        logger.info("Getting bookings for hotel %s with status %s", hotel_id, status)
        try:
            return await Booking.find(
                Booking.hotel_id == hotel_id,
                Booking.status == status
            ).to_list()
        except Exception as e:
            logger.error("Failed to get bookings by status: %s", e)
            raise

    @staticmethod
    async def check_suite_availability(
        suite_id: str,
        check_in: datetime,
        check_out: datetime
    ) -> bool:
        """
        Check if a suite is available for the given date range.
        Returns True if available, False if there are conflicting bookings.
        """
        logger.info("Checking suite availability: %s from %s to %s", suite_id, check_in, check_out)
        try:
            # Find any overlapping bookings that are not cancelled
            # A booking overlaps if:
            # existing_check_in < new_check_out AND existing_check_out > new_check_in
            conflicting_bookings = await Booking.find(
                Booking.suite_id == suite_id,
                NotIn(Booking.status, [BookingStatus.CANCELLED, BookingStatus.COMPLETED, BookingStatus.CHECKED_OUT]),
                Booking.check_in_date < check_out,
                Booking.check_out_date > check_in
            ).to_list()

            return len(conflicting_bookings) == 0
        except Exception as e:
            logger.error("Failed to check suite availability: %s", e)
            raise

    @staticmethod
    async def update_booking(booking_id: str, update_data: dict) -> Booking:
        """Update a booking with the given data"""
        logger.info("Updating booking: %s", booking_id)
        try:
            booking = await Booking.get(booking_id)
            if not booking:
                raise ValueError("Booking not found")

            if not update_data:
                raise ValueError("No data provided for update")

            # Update fields
            for key, value in update_data.items():
                if key in Booking.model_fields and key not in ["id", "_id", "createdAt"]:
                    setattr(booking, key, value)

            booking.updatedAt = datetime.now()
            await booking.save()
            return booking
        except ValueError:
            raise
        except Exception as e:
            logger.error("Failed to update booking: %s", e)
            raise

