import pytest

from app.repositories.hotel import HotelRepository
from app.models.hotel import HotelSuite, Hotel
from app.models.money import Money


@pytest.fixture
async def setup_new_hotel():
    data = {
        "name": "demo globus hotel",
        "address": "Setup Address",
        "email_address": "globus hotel",
        "phone_number": "0987654321",
        "state": "Setup State",
        "country": "Setup Country",
        "lga": "Setup LGA",
        "registration_type": "CAC",
        "registration_image_link": "http://example.com/setup_image.jpg",
        "owner_id": "setup_owner",
        "is_approved": True
    }
    hotel_input = Hotel(**data)
    hotel = await HotelRepository.create_hotel(hotel_input)
    yield hotel
    await hotel.delete()


class TestHotelSuiteRepository:

    @pytest.mark.anyio
    async def test_create_hotel(self):
        data = {
            "name": "Hotel 1",
            "address": "Address 1",
            "email_address": "test@email.com",
            "phone_number": "1234567890",
            "state": "State 1",
            "country": "Country 1",
            "lga": "LGA 1",
            "registration_type": "CAC",
            "registration_image_link": "http://example.com/image.jpg",
            "owner_id": "1",
            "is_approved": True
        }
        hotel_input = Hotel(**data)
        hotel = await HotelRepository.create_hotel(hotel_input)
        assert hotel.name == data["name"]
        assert hotel.email_address == data["email_address"]
        assert hotel.owner_id == data["owner_id"]
        assert hotel.is_approved == data["is_approved"]

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
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
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
    async def test_update_hotel_suite(self, setup_new_hotel):
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
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        assert hotel_suite.description == data["description"]
        assert hotel_suite.room_number == data["room_number"]
        assert hotel_suite.facilities == data["facilities"]

        data["name"] = "Suite 2"
        data["room_type"] = "VVIP"
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelRepository.update_hotel_suite(str(hotel_suite.id), suite_input.model_dump())
        assert hotel_suite.name == data["name"]
        assert hotel_suite.room_type == data["room_type"]

    @pytest.mark.anyio
    async def test_update_hotel_suite_empty_data(self, setup_new_hotel):
        hotel = setup_new_hotel
        data = {
            "hotel_id": str(hotel.id),
            "name": "Suite X",
            "price": Money("2000000.00"),
            "description": "The best suite in the hotel",
            "room_number": 1,
            "room_type": "Deluxe",
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        
        with pytest.raises(ValueError, match="No data provided for update"):
            await HotelRepository.update_hotel_suite(str(hotel_suite.id), {})

    @pytest.mark.anyio
    async def test_update_hotel_suite_invalid_fields(self, setup_new_hotel):
        hotel = setup_new_hotel
        data = {
            "hotel_id": str(hotel.id),
            "name": "Suite 1",
            "room_type": "Regular",
            "price": Money("100.00"),
            "description": "Description 1",
            "room_number": 1,
            "facilities": ["Playstation", "TV", "Air Conditioning", "Mini Bar", "Balcony", "Safe"]
        }
        suite_input = HotelSuite(**data)
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        
        with pytest.raises(ValueError, match="No valid fields provided for update"):
            await HotelRepository.update_hotel_suite(str(hotel_suite.id), {"invalid_field": "value"})

    @pytest.mark.anyio
    async def test_delete_hotel_suite(self, setup_new_hotel):
        hotel = setup_new_hotel
        data = {
            "hotel_id": str(hotel.id),
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

        deleted_suite = await HotelRepository.delete_hotel_suite(str(hotel_suite.id))
        assert deleted_suite.id == hotel_suite.id
    
    @pytest.mark.anyio
    async def test_get_suite_by_room_type_and_hotel_id(self, setup_new_hotel):
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
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]

        suite = await HotelRepository.get_suite_by_room_type_and_hotel_id("Regular", hotel.id)
        assert suite[0].id == hotel_suite.id

    @pytest.mark.anyio
    async def test_get_all_hotel_suites(self):
        suites = await HotelRepository.get_all_hotel_suites()
        assert isinstance(suites, list)
        assert len(suites) > 1
    
    @pytest.mark.anyio
    async def test_get_suites_by_price_range(self):
        suites = await HotelRepository.get_suites_by_price_range(100, 1000)
        assert isinstance(suites, list)
        assert len(suites) > 1

    @pytest.mark.anyio
    async def test_get_hotel_suite_by_facility(self, setup_new_hotel):
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
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        assert hotel_suite.description == data["description"]
        assert hotel_suite.room_number == data["room_number"]
        assert hotel_suite.facilities == data["facilities"]

        fetched_hotel_suite = await HotelRepository.get_suite_by_facility(hotel_suite.facilities[0])
        assert fetched_hotel_suite[-1].id == hotel_suite.id
        assert fetched_hotel_suite[-1].name == hotel_suite.name
        print(fetched_hotel_suite)
    
    @pytest.mark.anyio
    async def test_get_suite_by_room_number(self, setup_new_hotel):
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
        hotel_suite = await HotelRepository.create_hotel_suite(suite_input)
        assert hotel_suite.name == data["name"]
        assert hotel_suite.price == data["price"]
        assert hotel_suite.description == data["description"]
        assert hotel_suite.room_number == data["room_number"]
        assert hotel_suite.facilities == data["facilities"]

        fetched_hotel_suite = await HotelRepository.get_suite_by_room_number(hotel_suite.room_number, hotel.id)
        assert fetched_hotel_suite.id == hotel_suite.id
        assert fetched_hotel_suite.name == hotel_suite.name


class TestMerchantHotelRepository:
    """Tests for merchant/owner specific hotel repository methods"""

    @pytest.mark.anyio
    async def test_get_hotels_by_owner_id(self, setup_new_hotel):
        """Test retrieving all hotels owned by a specific merchant"""
        hotel = setup_new_hotel
        owner_id = hotel.owner_id

        hotels = await HotelRepository.get_hotels_by_owner_id(owner_id)

        assert isinstance(hotels, list)
        assert len(hotels) >= 1
        assert all(h.owner_id == owner_id for h in hotels)

    @pytest.mark.anyio
    async def test_get_hotels_by_owner_id_empty(self):
        """Test getting hotels for owner with no hotels"""
        hotels = await HotelRepository.get_hotels_by_owner_id("nonexistent_owner_12345")

        assert isinstance(hotels, list)
        assert len(hotels) == 0

    @pytest.mark.anyio
    async def test_get_hotels_by_owner_id_invalid(self):
        """Test getting hotels with invalid owner_id"""
        with pytest.raises(ValueError, match="Invalid owner_id"):
            await HotelRepository.get_hotels_by_owner_id("")

        with pytest.raises(ValueError, match="Invalid owner_id"):
            await HotelRepository.get_hotels_by_owner_id(None)

    @pytest.mark.anyio
    async def test_update_hotel(self, setup_new_hotel):
        """Test updating hotel details"""
        hotel = setup_new_hotel

        update_data = {
            "name": "Updated Hotel Name",
            "address": "456 New Address Street",
            "phone_number": "9876543210"
        }

        updated_hotel = await HotelRepository.update_hotel(str(hotel.id), update_data)

        assert updated_hotel.name == "Updated Hotel Name"
        assert updated_hotel.address == "456 New Address Street"
        assert updated_hotel.phone_number == "9876543210"
        # Ensure other fields remain unchanged
        assert updated_hotel.owner_id == hotel.owner_id
        assert updated_hotel.email_address == hotel.email_address

    @pytest.mark.anyio
    async def test_update_hotel_not_found(self):
        """Test updating a non-existent hotel"""
        with pytest.raises(ValueError, match="Hotel not found"):
            await HotelRepository.update_hotel("000000000000000000000000", {"name": "Test"})

    @pytest.mark.anyio
    async def test_update_hotel_empty_data(self, setup_new_hotel):
        """Test updating hotel with empty data"""
        hotel = setup_new_hotel

        with pytest.raises(ValueError, match="No data provided for update"):
            await HotelRepository.update_hotel(str(hotel.id), {})

    @pytest.mark.anyio
    async def test_toggle_hotel_availability_close(self, setup_new_hotel):
        """Test closing a hotel for business"""
        hotel = setup_new_hotel
        assert hotel.is_open is True  # Should be open by default

        updated_hotel = await HotelRepository.toggle_hotel_availability(str(hotel.id), False)

        assert updated_hotel.is_open is False

    @pytest.mark.anyio
    async def test_toggle_hotel_availability_open(self, setup_new_hotel):
        """Test opening a hotel for business"""
        hotel = setup_new_hotel
        # First close it
        await HotelRepository.toggle_hotel_availability(str(hotel.id), False)

        # Then open it
        updated_hotel = await HotelRepository.toggle_hotel_availability(str(hotel.id), True)

        assert updated_hotel.is_open is True

    @pytest.mark.anyio
    async def test_toggle_hotel_availability_not_found(self):
        """Test toggling availability for non-existent hotel"""
        with pytest.raises(ValueError, match="Hotel not found"):
            await HotelRepository.toggle_hotel_availability("000000000000000000000000", False)

    @pytest.mark.anyio
    async def test_get_hotel_by_id(self, setup_new_hotel):
        """Test getting a hotel by its ID"""
        hotel = setup_new_hotel

        fetched_hotel = await HotelRepository.get_hotel_by_id(str(hotel.id))

        assert fetched_hotel is not None
        assert fetched_hotel.id == hotel.id
        assert fetched_hotel.name == hotel.name

    @pytest.mark.anyio
    async def test_get_hotel_by_id_not_found(self):
        """Test getting a hotel that doesn't exist"""
        result = await HotelRepository.get_hotel_by_id("000000000000000000000000")
        assert result is None
