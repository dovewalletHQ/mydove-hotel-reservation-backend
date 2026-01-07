from app.repositories.hotel import HotelRepository
from app.models.hotel import HotelSuite


class HotelSuiteService:
    @staticmethod
    async def create_hotel_suite(hotel_suite: HotelSuite) -> HotelSuite:
        await hotel_suite.save()
        return hotel_suite
    
    @staticmethod
    async def get_hotel_suite_by_id(id: int) -> HotelSuite:
        if id is None:
            raise ValueError("Invalid id")
        return await HotelRepository.get_hotel_suite_by_id(id)

    @staticmethod
    async def update_hotel_suite(id: int, hotel_suite: HotelSuite) -> HotelSuite:
        if id is None:
            raise ValueError("Invalid id")
        return await HotelRepository.update_hotel_suite(id, hotel_suite)
