"""Hotel Service - Business logic layer for general hotel operations"""

from typing import Dict, List, Optional, Any

from app.core.logger import setup_logger
from app.repositories.hotel import HotelRepository
from app.models.hotel import Hotel


logger = setup_logger(name="hotel_service")


class HotelService:
    """Service for handling general hotel operations (public-facing)"""

    @staticmethod
    async def create_hotel(hotel: Hotel) -> Hotel:
        """Create a new hotel"""
        if not hotel.name or not hotel.name.strip():
            raise ValueError("Hotel name cannot be empty")

        if not hotel.owner_id or not hotel.owner_id.strip():
            raise ValueError("Owner ID cannot be empty")

        logger.info("Creating hotel: %s", hotel.name)
        return await HotelRepository.create_hotel(hotel)

    @staticmethod
    async def get_all_hotels(
        skip: int = 0,
        limit: int = 40,
        is_approved: Optional[bool] = None,
        is_open: Optional[bool] = None,
        state: Optional[str] = None,
        lga: Optional[str] = None,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_km: Optional[float] = 10.0,
    ) -> List[Hotel]:
        """Get all hotels with filters"""
        logger.info("Getting all hotels with filters")
        return await HotelRepository.get_hotels(
            skip=skip,
            limit=limit,
            is_approved=is_approved,
            is_open=is_open,
            state=state,
            lga=lga,
            city=city,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km,
        )

    @staticmethod
    async def get_hotel_by_id(hotel_id: str) -> Optional[Hotel]:
        """Get a hotel by its ID"""
        if not hotel_id or not hotel_id.strip():
            raise ValueError("Hotel ID cannot be empty")

        logger.info("Getting hotel by id: %s", hotel_id)
        return await HotelRepository.get_hotel_by_id(hotel_id)

    @staticmethod
    async def get_hotels_by_owner(owner_id: str) -> List[Hotel]:
        """Get all hotels owned by a specific owner"""
        if not owner_id or not owner_id.strip():
            raise ValueError("Owner ID cannot be empty")

        logger.info("Getting hotels by owner: %s", owner_id)
        return await HotelRepository.get_hotels_by_owner_id(owner_id)

    @staticmethod
    async def update_hotel(hotel_id: str, update_data: Dict[str, Any]) -> Optional[Hotel]:
        """Update hotel details"""
        if not hotel_id or not hotel_id.strip():
            raise ValueError("Hotel ID cannot be empty")

        if not update_data:
            raise ValueError("No data provided for update")

        logger.info("Updating hotel: %s", hotel_id)
        return await HotelRepository.update_hotel(hotel_id, update_data)

    @staticmethod
    async def delete_hotel(hotel_id: str) -> bool:
        """Delete a hotel by its ID"""
        if not hotel_id or not hotel_id.strip():
            raise ValueError("Hotel ID cannot be empty")

        hotel = await HotelRepository.get_hotel_by_id(hotel_id)
        if not hotel:
            return False

        logger.info("Deleting hotel: %s", hotel_id)
        await hotel.delete()
        return True

