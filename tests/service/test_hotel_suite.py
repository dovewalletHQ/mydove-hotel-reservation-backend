from app.services.hotel_suites import HotelSuiteService
from app.models.hotel import HotelSuite
from app.models.money import Money


import pytest

class TestHotelSuite:
    @pytest.mark.anyio
    async def test_create_hotel_suite(self):
        data = {
            "hotel_id": 1,
            "name": "Suite 1",
            "price": Money("100.00"),
            "description": "Description 1",
            "room_number": 1,
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelSuiteService.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        assert hotel_suite.description == data["description"]
        assert hotel_suite.room_number == data["room_number"]
        assert hotel_suite.facilities == data["facilities"]
    
    @pytest.mark.anyio
    async def test_get_hotel_suite_by_id(self):
        data = {
            "hotel_id": 1,
            "name": "Suite 1",
            "price": Money("100.00"),
            "description": "Description 1",
            "room_number": 1,
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelSuiteService.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        assert hotel_suite.description == data["description"]
        assert hotel_suite.room_number == data["room_number"]
        assert hotel_suite.facilities == data["facilities"]
