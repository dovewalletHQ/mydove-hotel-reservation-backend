from app.repositories.hotel import HotelRepository
from app.models.hotel import HotelSuite


class HotelSuiteService:
    @staticmethod
    async def create_hotel_suite(hotel_suite: HotelSuite) -> HotelSuite:

        await hotel_suite.save()
        return hotel_suite
    
    @staticmethod
    async def get_hotel_suite_by_id(id: str) -> HotelSuite:
        if id is None:
            raise ValueError("Invalid id")
        return await HotelRepository.get_hotel_suite_by_id(id)

    @staticmethod
    async def update_hotel_suite(id: str, hotel_suite: HotelSuite) -> HotelSuite:
        if id is None:
            raise ValueError("Invalid id")
        return await HotelRepository.update_hotel_suite(id, hotel_suite)
    
    @staticmethod
    async def delete_hotel_suite(id: str) -> None:
        if id is None:
            raise ValueError("Invalid id")
        await HotelRepository.delete_hotel_suite(id)
    
    @staticmethod
    async def get_all_hotel_suites() -> list[HotelSuite]:
        return await HotelRepository.get_all_hotel_suites()

    @staticmethod
    async def get_hotel_suites_by_hotel_id(id: str) -> list[HotelSuite]:
        if id is None:
            raise ValueError("Invalid id")
        return await HotelRepository.get_hotel_suites_by_hotel_id(id)
    
    