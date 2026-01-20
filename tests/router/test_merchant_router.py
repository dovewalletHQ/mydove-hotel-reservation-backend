"""Tests for Merchant Router - API endpoint tests"""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app
from app.models.hotel import Hotel, HotelSuite
from app.models.money import Money
from app.repositories.hotel import HotelRepository


@pytest.fixture
async def test_client():
    """Create an async test client"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
async def setup_merchant_hotel():
    """Setup a merchant with a hotel and suites for router testing"""
    owner_id = "router_test_merchant_789"

    hotel_data = {
        "name": "Router Test Hotel",
        "address": "123 Router Street",
        "email_address": "router@testhotel.com",
        "phone_number": "08012345678",
        "state": "Lagos",
        "country": "Nigeria",
        "lga": "Ikeja",
        "registration_type": "CAC",
        "registration_image_link": "http://example.com/cac.jpg",
        "owner_id": owner_id,
        "is_approved": True,
        "is_open": True
    }
    hotel = await HotelRepository.create_hotel(Hotel(**hotel_data))

    # Create a suite
    suite_data = {
        "hotel_id": str(hotel.id),
        "name": "Standard Room 101",
        "price": Money("150.00"),
        "description": "A comfortable standard room",
        "room_number": 101,
        "facilities": ["WiFi", "TV", "AC"],
        "is_available": True
    }
    suite = await HotelRepository.create_hotel_suite(HotelSuite(**suite_data))

    yield {"hotel": hotel, "suite": suite, "owner_id": owner_id}

    # Cleanup
    await suite.delete()
    await hotel.delete()


class TestMerchantRouter:

    @pytest.mark.anyio
    async def test_get_merchant_hotels(self, test_client, setup_merchant_hotel):
        """Test GET /merchants/{owner_id}/hotels"""
        owner_id = setup_merchant_hotel["owner_id"]

        response = await test_client.get(f"/api/v1/merchants/{owner_id}/hotels")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(h["owner_id"] == owner_id for h in data)

    @pytest.mark.anyio
    async def test_get_merchant_hotels_invalid_owner(self, test_client):
        """Test GET /merchants/{owner_id}/hotels with invalid owner"""
        response = await test_client.get("/api/v1/merchants/ /hotels")

        assert response.status_code == 400

    @pytest.mark.anyio
    async def test_create_hotel(self, test_client):
        """Test POST /merchants/{owner_id}/hotels"""
        owner_id = "new_merchant_create_test"
        hotel_data = {
            "name": "New Created Hotel",
            "address": "456 New Street",
            "email_address": "new@hotel.com",
            "phone_number": "08099999999",
            "state": "Abuja",
            "country": "Nigeria",
            "lga": "Garki",
            "registration_image_link": "http://example.com/cac.jpg"
        }

        response = await test_client.post(
            f"/api/v1/merchants/{owner_id}/hotels",
            json=hotel_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Created Hotel"
        assert data["owner_id"] == owner_id
        assert data["is_approved"] is False  # New hotels need admin approval

        # Cleanup
        hotel = await Hotel.get(data["_id"])
        if hotel:
            await hotel.delete()

    @pytest.mark.anyio
    async def test_update_hotel(self, test_client, setup_merchant_hotel):
        """Test PATCH /merchants/{owner_id}/hotels/{hotel_id}"""
        owner_id = setup_merchant_hotel["owner_id"]
        hotel_id = str(setup_merchant_hotel["hotel"].id)

        update_data = {
            "name": "Updated Router Hotel Name",
            "address": "Updated Address 999"
        }

        response = await test_client.patch(
            f"/api/v1/merchants/{owner_id}/hotels/{hotel_id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Router Hotel Name"

    @pytest.mark.anyio
    async def test_update_hotel_not_owner(self, test_client, setup_merchant_hotel):
        """Test PATCH /merchants/{owner_id}/hotels/{hotel_id} with wrong owner"""
        hotel_id = str(setup_merchant_hotel["hotel"].id)

        update_data = {"name": "Unauthorized Update"}

        response = await test_client.patch(
            f"/api/v1/merchants/wrong_owner/hotels/{hotel_id}",
            json=update_data
        )

        assert response.status_code == 403

    @pytest.mark.anyio
    async def test_set_hotel_availability(self, test_client, setup_merchant_hotel):
        """Test PATCH /merchants/{owner_id}/hotels/{hotel_id}/availability"""
        owner_id = setup_merchant_hotel["owner_id"]
        hotel_id = str(setup_merchant_hotel["hotel"].id)

        # Close the hotel
        response = await test_client.patch(
            f"/api/v1/merchants/{owner_id}/hotels/{hotel_id}/availability",
            json={"is_open": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_open"] is False

        # Reopen the hotel
        response = await test_client.patch(
            f"/api/v1/merchants/{owner_id}/hotels/{hotel_id}/availability",
            json={"is_open": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_open"] is True

    @pytest.mark.anyio
    async def test_get_merchant_hotel_suites(self, test_client, setup_merchant_hotel):
        """Test GET /merchants/{owner_id}/hotels/{hotel_id}/suites"""
        owner_id = setup_merchant_hotel["owner_id"]
        hotel_id = str(setup_merchant_hotel["hotel"].id)

        response = await test_client.get(
            f"/api/v1/merchants/{owner_id}/hotels/{hotel_id}/suites"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.anyio
    async def test_create_suite(self, test_client, setup_merchant_hotel):
        """Test POST /merchants/{owner_id}/hotels/{hotel_id}/suites"""
        owner_id = setup_merchant_hotel["owner_id"]
        hotel_id = str(setup_merchant_hotel["hotel"].id)

        suite_data = {
            "name": "Deluxe Room 201",
            "price": 250.00,
            "description": "A deluxe room with great views",
            "room_number": 201,
            "room_type": "Deluxe",
            "facilities": ["WiFi", "TV", "AC", "Mini Bar"],
            "is_available": True
        }

        response = await test_client.post(
            f"/api/v1/merchants/{owner_id}/hotels/{hotel_id}/suites",
            json=suite_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Deluxe Room 201"
        assert data["hotel_id"] == hotel_id

        # Cleanup
        suite = await HotelSuite.get(data["_id"])
        if suite:
            await suite.delete()

    @pytest.mark.anyio
    async def test_set_suite_availability(self, test_client, setup_merchant_hotel):
        """Test PATCH /merchants/{owner_id}/hotels/{hotel_id}/suites/{suite_id}/availability"""
        owner_id = setup_merchant_hotel["owner_id"]
        hotel_id = str(setup_merchant_hotel["hotel"].id)
        suite_id = str(setup_merchant_hotel["suite"].id)

        # Make unavailable
        response = await test_client.patch(
            f"/api/v1/merchants/{owner_id}/hotels/{hotel_id}/suites/{suite_id}/availability",
            json={"is_available": False}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_available"] is False

    @pytest.mark.anyio
    async def test_get_merchant_bookings(self, test_client, setup_merchant_hotel):
        """Test GET /merchants/{owner_id}/bookings"""
        owner_id = setup_merchant_hotel["owner_id"]

        response = await test_client.get(f"/api/v1/merchants/{owner_id}/bookings")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.anyio
    async def test_get_hotel_bookings(self, test_client, setup_merchant_hotel):
        """Test GET /merchants/{owner_id}/hotels/{hotel_id}/bookings"""
        owner_id = setup_merchant_hotel["owner_id"]
        hotel_id = str(setup_merchant_hotel["hotel"].id)

        response = await test_client.get(
            f"/api/v1/merchants/{owner_id}/hotels/{hotel_id}/bookings"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.anyio
    async def test_get_revenue_summary(self, test_client, setup_merchant_hotel):
        """Test GET /merchants/{owner_id}/revenue-summary"""
        owner_id = setup_merchant_hotel["owner_id"]

        response = await test_client.get(f"/api/v1/merchants/{owner_id}/revenue-summary")

        assert response.status_code == 200
        data = response.json()
        assert "total_hotels" in data
        assert "total_bookings" in data
        assert "total_revenue" in data

    @pytest.mark.anyio
    async def test_get_hotel_dashboard(self, test_client, setup_merchant_hotel):
        """Test GET /merchants/{owner_id}/hotels/{hotel_id}/dashboard"""
        owner_id = setup_merchant_hotel["owner_id"]
        hotel_id = str(setup_merchant_hotel["hotel"].id)

        response = await test_client.get(
            f"/api/v1/merchants/{owner_id}/hotels/{hotel_id}/dashboard"
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_suites" in data
        assert "available_suites" in data
        assert "total_bookings" in data

