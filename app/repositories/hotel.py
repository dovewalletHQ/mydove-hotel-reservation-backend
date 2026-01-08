from typing import Union, Dict, Any, List

from beanie.odm.operators.find.comparison import In
from bson import ObjectId

from app.models.hotel import HotelSuite, Hotel
from app.core.logger import logger

class HotelRepository: 
    """This handles the hotel reservation logic"""

    @staticmethod
    async def create_hotel(hotel: Hotel) -> Hotel:
        logger.info("Creating hotel: %s", hotel)
        return await hotel.save()

    @staticmethod
    async def create_hotel_suite(hotel_suite: HotelSuite) -> HotelSuite:
        # get hotel first to see if hotel is approved and see if the user_id creating the hotel is the same as the owner id
        hotel = await HotelRepository.get_hotel_owner_by_hotel_id(hotel_suite.hotel_id)
        if hotel is None:
            raise ValueError("Hotel not found")
        if not hotel.is_approved:
            raise ValueError("Hotel owner is not approved")

        logger.info("Creating hotel suite: %s", hotel_suite)
        return await hotel_suite.save()

    @staticmethod
    async def get_hotel_suite_by_id(id: str) -> HotelSuite:
        logger.info("Getting hotel suite by id: %s", id)
        try:
            return await HotelSuite.get(id)
        except Exception as e:
            logger.error("Failed to get hotel suite by id: %s", e)
            raise

    @staticmethod
    async def get_all_hotel_suites() -> List[HotelSuite]:
        logger.info("Getting all hotel suites")
        try:
            return await HotelSuite.find().to_list()
        except Exception as e:
            logger.error("Failed to get all hotel suites: %s", e)
            raise

    @staticmethod
    async def get_available_hotel_suites() -> List[HotelSuite]:
        logger.info("Getting available hotel suites")
        try:
            return await HotelSuite.find_all(HotelSuite.is_available == True).to_list()
        except Exception as e:
            logger.error("Failed to get available hotel suites: %s", e)
            raise

    @staticmethod
    async def update_hotel_suite(id: str, update_data: Union[HotelSuite, Dict[str, Any]]) -> HotelSuite:
        """Update Hotel suite using the suite id"""
        logger.info("Updating hotel suite: %s", update_data)
        try:
            existing_suite = await HotelSuite.get(id)
            if not existing_suite:
                 raise ValueError("Hotel suite not found")

            data_to_update = update_data
            if isinstance(update_data, HotelSuite):
                data_to_update = update_data.model_dump(exclude_unset=True)

            if not data_to_update:
                 raise ValueError("No data provided for update")

            # Update fields
            updated = False
            for key, value in data_to_update.items():
                if key in HotelSuite.model_fields and key not in ["id", "_id", "createdAt"]:
                     setattr(existing_suite, key, value)
                     updated = True

            if not updated:
                raise ValueError("No valid fields provided for update")
            
            await existing_suite.save()
            return existing_suite

        except Exception as e:
            logger.error("Failed to update hotel suite: %s", e)
            raise

    @staticmethod
    async def delete_hotel_suite(id: str) -> HotelSuite:
        """Delete Hotel suite using the suite id"""
        logger.info("Deleting hotel suite: %s", id)
        try:
            hotel_suite = await HotelSuite.get(id)
            if not hotel_suite:
                raise ValueError("Hotel suite not found")
            await hotel_suite.delete()
            return hotel_suite
        except Exception as e:
            logger.error("Failed to delete hotel suite: %s", e)
            raise

    @staticmethod
    async def get_hotel_owner_by_hotel_id(id: str) -> Hotel:
        """Get hotel owner by hotel id"""
        logger.info("Getting hotel owner by hotel id: %s", id)
        try:
            return await Hotel.find_one(Hotel.id == ObjectId(id))
        except Exception as e:
            logger.error("Failed to get hotel owner by hotel id: %s", e)
            raise

    @staticmethod
    async def get_suite_by_room_type_and_hotel_id(room_type: str, hotel_id: str) -> List[HotelSuite]:
        """Get suite by room type and hotel id"""
        logger.info("Getting suite by room type and hotel id: %s", room_type)
        try:
            return await HotelSuite.find(HotelSuite.room_type == room_type, HotelSuite.hotel_id == str(hotel_id)).to_list()
        except Exception as e:
            logger.error("Failed to get suite by room type and hotel id: %s", e)
            raise

    @staticmethod
    async def get_suites_by_price_range(min_price: float, max_price: float) -> List[HotelSuite]:
        """Get suites by price range"""
        logger.info("Getting suites by price range: %s", min_price)
        try:
            return await HotelSuite.find(HotelSuite.price >= min_price, HotelSuite.price <= max_price).to_list()
        except Exception as e:
            logger.error("Failed to get suites by price range: %s", e)
            raise
    
    @staticmethod
    async def get_suite_by_facility(facility: str) -> List[HotelSuite]:
        """Get suite by facility"""
        logger.info("Getting suite by facility: %s", facility)
        try:
            return await HotelSuite.find(In(HotelSuite.facilities, [facility])).to_list()
        except Exception as e:
            logger.error("Failed to get suite by facility: %s", e)
            raise
    
    @staticmethod
    async def get_suite_by_room_number(room_number: int) -> List[HotelSuite]:
        """Get suite by room number"""
        logger.info("Getting suite by room number: %s", room_number)
        try:
            return await HotelSuite.find(HotelSuite.room_number == room_number).to_list()
        except Exception as e:
            logger.error("Failed to get suite by room number: %s", e)
            raise
