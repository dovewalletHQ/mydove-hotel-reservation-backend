import pytest

from app.repositories.hotel import HotelRepository
from app.models.hotel import HotelSuite
from app.models.money import Money

class TestHotelSuiteRepository:
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
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
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
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"],
            "is_available": True
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        assert hotel_suite.description == data["description"]
        assert hotel_suite.room_number == data["room_number"]
        assert hotel_suite.facilities == data["facilities"]
    
    @pytest.mark.anyio
    async def test_update_hotel_suite(self):
        data = {
            "hotel_id": 1,
            "name": "Suite 1",
            "price": Money("100.00"),
            "description": "Description 1",
            "room_number": 1,
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        assert hotel_suite.description == data["description"]
        assert hotel_suite.room_number == data["room_number"]
        assert hotel_suite.facilities == data["facilities"]

        data["name"] = "Suite 2"
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelRepository.update_hotel_suite(str(hotel_suite.id), suite_input.model_dump())
        assert hotel_suite.name == data["name"]

    @pytest.mark.anyio
    async def test_update_hotel_suite_empty_data(self):
        data = {
            "hotel_id": 1,
            "name": "Suite 1",
            "price": Money("100.00"),
            "description": "Description 1",
            "room_number": 1,
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        
        with pytest.raises(ValueError, match="No data provided for update"):
            await HotelRepository.update_hotel_suite(str(hotel_suite.id), {})

    @pytest.mark.anyio
    async def test_delete_hotel_suite(self):
        data = {
            "hotel_id": 1,
            "name": "Suite 1",
            "price": Money("100.00"),
            "description": "Description 1000",
            "room_number": 1,
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        assert hotel_suite.description == data["description"]
        assert hotel_suite.room_number == data["room_number"]
        assert hotel_suite.facilities == data["facilities"]