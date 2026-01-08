from app.services.hotel_suites import HotelSuiteService
from app.models.hotel import HotelSuite
from app.models.money import Money
from tests.repository.test_hotel_repository import setup_new_hotel


import pytest

class TestHotelSuite:
    @pytest.mark.anyio
    async def test_create_hotel_suite(self, setup_new_hotel):
        hotel = setup_new_hotel
        data = {
            "hotel_id": str(hotel.id),
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
    async def test_get_hotel_suite_by_id(self, setup_new_hotel):
        hotel = setup_new_hotel
        data = {
            "hotel_id": str(hotel.id),
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

        fetched_hotel_suite = await HotelSuiteService.get_hotel_suite_by_id(hotel_suite.id)
        assert fetched_hotel_suite.id == hotel_suite.id
        assert fetched_hotel_suite.name == hotel_suite.name
    
    @pytest.mark.anyio
    async def test_update_hotel_suite(self, setup_new_hotel):
        hotel = setup_new_hotel
        data = {
            "hotel_id": str(hotel.id),
            "name": "Suite 100",
            "price": Money("100.00"),
            "description": "Highly comfortable suite",
            "room_number": 1,
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelSuiteService.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        
        updated_data = {
            "hotel_id": str(hotel.id),
            "name": "Suite 2",
            "price": Money("200.00"),
            "description": "Description 2",
            "room_number": 2,
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        updated_suite_input = HotelSuite(**updated_data)
        updated_hotel_suite = await HotelSuiteService.update_hotel_suite(hotel_suite.id, updated_suite_input)
        assert updated_hotel_suite.name == updated_data["name"]
        assert updated_hotel_suite.price == updated_data["price"]
