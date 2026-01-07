from typing import Union, Dict, Any
from bson import ObjectId

from app.models.hotel import HotelSuite
from app.core.logger import logger

class HotelRepository: 
    """This handles the hotel reservation logic"""

    @staticmethod
    async def create_hotel_suite(hotel_suite: HotelSuite) -> HotelSuite:
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
    async def get_all_hotel_suites() -> list[HotelSuite]:
        logger.info("Getting all hotel suites")
        try:
            return await HotelSuite.find_all().to_list()
        except Exception as e:
            logger.error("Failed to get all hotel suites: %s", e)
            raise

    @staticmethod
    async def get_available_hotel_suites() -> list[HotelSuite]:
        logger.info("Getting available hotel suites")
        try:
            return await HotelSuite.find_all(HotelSuite.is_available == True).to_list()
        except Exception as e:
            logger.error("Failed to get available hotel suites: %s", e)
            raise
    
    @staticmethod
    async def update_hotel_suite(id: str, update_data: Union[HotelSuite, Dict[str, Any]]) -> HotelSuite:
        logger.info("Updating hotel suite: %s", update_data)
        try:
            existing_suite = await HotelSuite.get(id)
            if not existing_suite:
                 raise ValueError("Hotel suite not found")

            data_to_update = update_data
            if isinstance(update_data, HotelSuite):
                data_to_update = update_data.model_dump(exclude_unset=True)
            elif isinstance(update_data, dict):
                 pass
            
            # Update fields
            for key, value in data_to_update.items():
                if hasattr(existing_suite, key):
                     setattr(existing_suite, key, value)
            
            await existing_suite.save()
            return existing_suite

        except Exception as e:
            logger.error("Failed to update hotel suite: %s", e)
            raise
    
    @staticmethod
    async def delete_hotel_suite(id: str) -> HotelSuite:
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