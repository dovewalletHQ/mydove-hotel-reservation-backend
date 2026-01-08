from app.repositories.hotel_profile import HotelProfileRepository
from app.models.hotel import HotelProfile
from app.core.logger import logger
from typing import Union

class HotelProfileService:
    @staticmethod
    async def create_hotel_profile(hotel_profile: HotelProfile) -> Union[HotelProfile, str]:
        if hotel_profile is None:
            return "Invalid hotel profile"
        logger.info("Creating hotel profile: %s", hotel_profile)
        return await HotelProfileRepository.create_hotel_profile(hotel_profile)
    
    @staticmethod
    async def get_hotel_profile_by_hotel_id(hotel_id: str) -> Union[HotelProfile, str]:
        if hotel_id is None:
            return "Invalid hotel id"
        logger.info("Getting hotel profile by hotel id: %s", hotel_id)
        return await HotelProfileRepository.get_hotel_profile_by_hotel_id(hotel_id)
    
    @staticmethod
    async def update_hotel_profile(hotel_profile: HotelProfile) -> Union[HotelProfile, str]:
        if hotel_profile is None:
            return "Invalid hotel profile"
        logger.info("Updating hotel profile: %s", hotel_profile)
        return await HotelProfileRepository.update_hotel_profile(hotel_profile)
    
    @staticmethod
    async def delete_hotel_profile(hotel_id: str) -> Union[HotelProfile, str]:
        if hotel_id is None:
            return "Invalid hotel id"
        logger.info("Deleting hotel profile: %s", hotel_id)
        return await HotelProfileRepository.delete_hotel_profile(hotel_id)