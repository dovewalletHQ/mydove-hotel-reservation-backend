from typing import Union, Dict, Any, List

from beanie.odm.operators.find.comparison import In
from bson import ObjectId
from datetime import datetime

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
    async def get_hotel_suites_by_id(hotel_id: str) -> List[HotelSuite]:
        """Get all hotel suites by hotel id"""
        if hotel_id is None or not hotel_id.strip():
            raise ValueError("Invalid hotel_id: hotel_id cannot be None or empty")

        logger.info("Getting hotel suites by hotel id: %s", hotel_id)
        try:
            return await HotelSuite.find(HotelSuite.hotel_id == str(hotel_id)).to_list()
        except Exception as e:
            logger.error("Failed to get hotel suites by hotel id: %s", e)
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
    async def get_available_hotel_suites_by_hotel_id(hotel_id: str) -> List[HotelSuite]:
        """Get all available hotel suites by hotel id"""
        logger.info("Getting available hotel suites")
        try:
            return await HotelSuite.find(HotelSuite.is_available == True, HotelSuite.hotel_id == str(hotel_id)).to_list()
        except Exception as e:
            logger.error("Failed to get available hotel suites: %s", e)
            raise
    
    @staticmethod
    async def get_unavailable_hotel_suites_by_hotel_id(hotel_id: str) -> List[HotelSuite]:
        """Get all unavailable hotel suites by hotel id"""
        logger.info("Getting unavailable hotel suites")
        try:
            return await HotelSuite.find(HotelSuite.is_available == False, HotelSuite.hotel_id == str(hotel_id)).to_list()
        except Exception as e:
            logger.error("Failed to get unavailable hotel suites: %s", e)
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
    async def get_suite_by_room_number(room_number: int, hotel_id: str) -> HotelSuite:
        """Get suite by room number"""
        logger.info("Getting suite by room number: %s", room_number)
        try:
            return await HotelSuite.find_one(HotelSuite.room_number == room_number, HotelSuite.hotel_id == str(hotel_id))
        except Exception as e:
            logger.error("Failed to get suite by room number: %s", e)
            raise

    @staticmethod
    async def delete_suite_by_room_number(room_number, hotel_id):
        """Delete suite by room number and hotel id"""
        logger.info("Deleting suite by room number: %s", room_number)
        try:
            return await HotelSuite.delete_one(HotelSuite.room_number == room_number, HotelSuite.hotel_id == str(hotel_id))
        except Exception as e:
            logger.error("Failed to delete suite by room number: %s", e)
            raise

    # =====================
    # Merchant/Owner Methods
    # =====================

    @staticmethod
    async def get_hotels_by_owner_id(owner_id: str) -> List[Hotel]:
        """Get all hotels owned by a specific merchant/owner"""
        if owner_id is None or not str(owner_id).strip():
            raise ValueError("Invalid owner_id: owner_id cannot be None or empty")

        logger.info("Getting hotels by owner id: %s", owner_id)
        try:
            return await Hotel.find(Hotel.owner_id == owner_id).to_list()
        except Exception as e:
            logger.error("Failed to get hotels by owner id: %s", e)
            raise

    @staticmethod
    async def get_hotel_by_id(hotel_id: str) -> Union[Hotel, None]:
        """Get a hotel by its ID"""
        logger.info("Getting hotel by id: %s", hotel_id)
        try:
            return await Hotel.get(hotel_id)
        except Exception as e:
            logger.error("Failed to get hotel by id: %s", e)
            return None

    @staticmethod
    async def update_hotel(hotel_id: str, update_data: dict) -> Hotel:
        """Update hotel details"""
        logger.info("Updating hotel: %s", hotel_id)
        try:

            hotel = await Hotel.get(hotel_id)
            if not hotel:
                raise ValueError("Hotel not found")

            if not update_data:
                raise ValueError("No data provided for update")

            # Update fields
            updated = False
            for key, value in update_data.items():
                if key in Hotel.model_fields and key not in ["id", "_id", "createdAt"]:
                    setattr(hotel, key, value)
                    updated = True

            if not updated:
                raise ValueError("No valid fields provided for update")

            hotel.updatedAt = datetime.now()
            await hotel.save()
            return hotel
        except ValueError:
            raise
        except Exception as e:
            logger.error("Failed to update hotel: %s", e)
            raise

    @staticmethod
    async def toggle_hotel_availability(hotel_id: str, is_open: bool) -> Hotel:
        """Toggle hotel open/closed status for the day"""
        logger.info("Toggling hotel availability: %s to %s", hotel_id, is_open)
        try:
            hotel = await Hotel.get(hotel_id)
            if not hotel:
                raise ValueError("Hotel not found")

            hotel.is_open = is_open
            hotel.updatedAt = datetime.now()
            await hotel.save()
            return hotel
        except ValueError:
            raise
        except Exception as e:
            logger.error("Failed to toggle hotel availability: %s", e)
            raise

