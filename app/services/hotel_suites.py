from datetime import datetime

from app.core.logger import setup_logger
from app.repositories.hotel import HotelRepository
from app.models.hotel import HotelSuite


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
