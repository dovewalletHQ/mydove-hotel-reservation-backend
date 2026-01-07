from app.models.hotel import HotelSuite


class HotelSuiteService:
    @staticmethod
    async def create_hotel_suite(hotel_suite: HotelSuite) -> HotelSuite:
        await hotel_suite.save()
        return hotel_suite
    
    @staticmethod
    async def get_hotel_suite_by_id(id: int) -> HotelSuite:
        return await HotelSuite.find_one(HotelSuite.id == id)
