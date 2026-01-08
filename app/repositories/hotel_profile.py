from typing import Union

from app.core.logger import logger
from datetime import datetime
from app.models.hotel import HotelProfile


class HotelProfileRepository:
    """Hotel profile repository"""
    @staticmethod
    async def create_hotel_profile(hotel_profile: HotelProfile) -> Union[HotelProfile | None]:
        """Create hotel profile"""
        logger.info("Creating hotel profile: %s", hotel_profile)
        return await hotel_profile.save()
    
    @staticmethod
    async def get_hotel_profile_by_hotel_id(hotel_id: str) -> Union[HotelProfile | None]:
        """Get hotel profile by hotel id"""
        logger.info("Getting hotel profile by hotel id: %s", hotel_id)
        try:
            return await HotelProfile.find_one(HotelProfile.hotel_id == hotel_id)
        except Exception as e:
            logger.error("Failed to get hotel profile by hotel id: %s", e)
            return None
    
    @staticmethod
    async def update_hotel_profile(hotel_profile: HotelProfile) -> Union[HotelProfile | None]:
        """Update hotel profile"""
        hotel_profile.updatedAt = datetime.now()
        logger.info("Updating hotel profile: %s", hotel_profile)
        try:
            return await hotel_profile.save()
        except Exception as e:
            logger.error("Failed to update hotel profile: %s", e)
            return None
    
    @staticmethod
    async def delete_hotel_profile(hotel_id: str) -> Union[HotelProfile | None]:
        """Delete hotel profile"""
        logger.info("Deleting hotel profile: %s", hotel_id)
        try:
            hotel_profile = await HotelProfile.find_one(HotelProfile.hotel_id == hotel_id)
            if not hotel_profile:
                logger.error("Hotel profile not found")
                return None
            await hotel_profile.delete()
            return hotel_profile
        except Exception as e:
            logger.error("Failed to delete hotel profile: %s", e)
            return None