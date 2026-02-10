from datetime import datetime
from typing import Optional

from app.core.logger import setup_logger
from app.models.booking import HotelSuiteBookingResponse, HotelSuiteBookingRequest
from app.repositories.hotel import HotelRepository
from app.models.hotel import HotelSuite
from app.services.booking import BookingService


logger = setup_logger(name="hotel_suite_service")

class HotelSuiteService:
    @staticmethod
    async def create_hotel_suite(hotel_suite: HotelSuite) -> HotelSuite:

        await hotel_suite.save()
        return hotel_suite
    
    @staticmethod
    async def get_hotel_suite_by_id(suite_id: str) -> HotelSuite:
        if suite_id is None or not suite_id.strip():
            raise ValueError("Invalid id: id cannot be None or empty")
        try:
            suite = await HotelRepository.get_hotel_suite_by_id(suite_id)
            if suite is None:
                raise ValueError(f"Hotel suite with id '{suite_id}' not found")
            return suite
        except Exception as e:
            logger.error("Error retrieving hotel suite by id '%s': %s", suite_id, e)
            raise

    @staticmethod
    async def update_hotel_suite(suite_id: str, hotel_suite: HotelSuite) -> HotelSuite:
        if suite_id is None or not suite_id.strip():
            raise ValueError("Invalid id: id cannot be None or empty")
        try:
            logger.info("Updating hotel suite with id '%s'", suite_id)
            hotel_suite.updatedAt = datetime.now()
            return await HotelRepository.update_hotel_suite(suite_id, hotel_suite)
        except Exception as e:
            logger.error("Error updating hotel suite with id '%s': %s", suite_id, e)
            raise

    @staticmethod
    async def delete_hotel_suite(suite_id: str) -> None:
        """Delete a hotel suite by its id"""
        if suite_id is None or not suite_id.strip():
            raise ValueError("Invalid hotel id: hotel id cannot be None or empty")
        try:
            await HotelRepository.delete_hotel_suite(suite_id)
        except Exception as e:
            logger.error("Error deleting hotel suite with id '%s': %s", suite_id, e)
            raise

    @staticmethod
    async def get_all_hotel_suites() -> list[HotelSuite]:
        """Get all hotel suites regardless of the hotel"""
        try:
            logger.info("Retrieving all hotel suites")
            suites = await HotelRepository.get_all_hotel_suites()
            return suites
        except Exception as e:
            logger.error("Error retrieving all hotel suites: %s", e)
            raise

    @staticmethod
    async def get_hotel_suites_by_hotel_id(hotel_id: str) -> list[HotelSuite]:
        """Get all hotel suites by hotel id"""
        if hotel_id is None or not hotel_id.strip():
            raise ValueError("Empty hotel id")
        return await HotelRepository.get_hotel_suites_by_id(hotel_id)

    @staticmethod
    async def get_suite_by_room_number(room_number: int, hotel_id: str) -> HotelSuite:
        """Get a hotel suite by its room number and hotel id"""
        if room_number is None or hotel_id is None:
            raise ValueError("Invalid room number or hotel id")
        return await HotelRepository.get_suite_by_room_number(room_number, hotel_id)

    @staticmethod
    async def delete_suite_by_id(suite_id: str) -> None:
        """Delete a hotel suite by its id"""
        if suite_id is None or not suite_id.strip():
            raise ValueError("Invalid suite id: suite id cannot be None or empty")
        try:
            logger.info("Deleting suite with id %s", suite_id)
            await HotelRepository.delete_hotel_suite(suite_id)
        except Exception as e:
            logger.error("Error deleting suite with id %s: %s", suite_id, e)
            raise
    
    @staticmethod
    async def delete_suite_by_room_number(room_number: int, hotel_id: str) -> None:
        """Delete a hotel suite by its room number and hotel id"""
        if room_number is None or hotel_id is None:
            raise ValueError("Invalid room number or hotel id")
        try:
            logger.info("Deleting suite with room number %s from hotel %s", room_number, hotel_id)
            await HotelRepository.delete_suite_by_room_number(room_number, hotel_id)
        except Exception as e:
            logger.error("Error deleting suite with room number %s from hotel %s: %s", room_number, hotel_id, e)
            raise

    @staticmethod
    async def change_suite_room_availability_by_hotel_id(hotel_id: str, suite_id: int, is_available: bool) -> HotelSuite:
        """Change suite room availability by hotel id"""
        if hotel_id is None:
            logger.error("Invalid hotel id")
            raise ValueError("Invalid hotel id")
        if suite_id <= 0:
            logger.error("Suite id must be a positive integer")
            raise ValueError("Suite id must be a positive integer")

        hotel_suite = await HotelRepository.get_suite_by_room_number(suite_id, hotel_id)
        if hotel_suite is None:
            logger.error("Suite with id '%s' not found", suite_id)
            raise ValueError("Suite not found")
        hotel_suite.is_available = is_available
        await hotel_suite.save()
        return hotel_suite

    @staticmethod
    async def book_suite(suite_id: str, request: HotelSuiteBookingRequest) -> Optional[HotelSuiteBookingResponse | None]:
        if suite_id is None or request is None:
            raise ValueError("Invalid suite id or request")
        
        # check if suite is available
        try:
            suite = await HotelRepository.get_hotel_suite_by_id(suite_id)
            if suite is None:
                logger.error("Suite with id '%s' not found", suite_id)
                raise ValueError("Suite not found")
            # check if the checking date is before the checkout date
            if request.check_in_date >= request.check_out_date:
                logger.error("Check-in date must be before check-out date")
                raise ValueError("Check-in date must be before check-out date")
            # check if there's a current booking but the new check-in date is before the current booking's check-out date
            booking = await BookingService.get_booking_by_suite_id(suite_id)
            if booking is not None:
                if request.check_in_date < booking.check_out_date:
                    logger.error("Check-in date must be after the current booking's check-out date")
                    raise ValueError("Check-in date must be after the current booking's check-out date")

            # booking suite for user
            booking = await BookingService.create_booking(request.model_dump())
            if booking is None:
                logger.error("Error booking suite with id '%s'", suite_id)
                raise ValueError("Error booking suite")
            suite.is_available = False
            await suite.save()
            return HotelSuiteBookingResponse(
                booking_id=str(booking.id),
                hotel_id=booking.hotel_id,
                suite_id=booking.suite_id,
                suite_room_number=suite.room_number,
                guest_name=booking.guest_name,
                guest_phone=booking.guest_phone,
                guest_email=booking.guest_email,
                check_in_date=booking.check_in_date,
                check_out_date=booking.check_out_date,
                booking_type=booking.booking_type,
                status=booking.status,
                total_amount=booking.total_amount,
                discount_amount=booking.discount_amount,
                final_amount=booking.total_amount - booking.discount_amount,
                number_of_guests=booking.number_of_guests,
                special_requests=booking.special_requests,
                booked_by_owner_id=booking.booked_by_owner_id
            )
        except ValueError as e:
            logger.error("Error booking suite with id '%s': %s", suite_id[:7], e)
            raise
        except Exception as e:
            logger.error("Error booking suite with id '%s': %s", suite_id[:7], e)
            raise
