"""Tests for Merchant Service - Following TDD approach"""

import pytest
from datetime import datetime, timedelta

from app.services.merchant import MerchantService
from app.services.booking import BookingService
from app.repositories.hotel import HotelRepository
from app.models.hotel import Hotel, HotelSuite
from app.models.booking import BookingType, BookingStatus
from app.models.money import Money


@pytest.fixture
async def setup_merchant_with_hotel():
    """Setup a merchant with a hotel and suites"""
    owner_id = "test_merchant_owner_456"

    hotel_data = {
        "name": "Merchant Service Test Hotel",
        "address": "789 Merchant Avenue",
        "email_address": "service@merchanthotel.com",
        "phone_number": "0812345678",
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

    # Create multiple suites
    suites = []
    for i in range(3):
        suite_data = {
            "hotel_id": str(hotel.id),
            "name": f"Room {301 + i}",
            "price": Money(str(100 + (i * 50))),
            "description": f"Room number {301 + i}",
            "room_number": 301 + i,
            "facilities": ["WiFi", "TV", "AC"],
            "is_available": True
        }
        suite = await HotelRepository.create_hotel_suite(HotelSuite(**suite_data))
        suites.append(suite)

    yield {"hotel": hotel, "suites": suites, "owner_id": owner_id}

    # Cleanup
    for suite in suites:
        await suite.delete()
    await hotel.delete()


class TestMerchantService:

    @pytest.mark.anyio
    async def test_get_merchant_hotels(self, setup_merchant_with_hotel):
        """Test getting all hotels owned by a merchant"""
        owner_id = setup_merchant_with_hotel["owner_id"]

        hotels = await MerchantService.get_merchant_hotels(owner_id)

        assert isinstance(hotels, list)
        assert len(hotels) >= 1
        assert all(h.owner_id == owner_id for h in hotels)

    @pytest.mark.anyio
    async def test_get_merchant_hotels_invalid_owner(self):
        """Test getting hotels with invalid owner ID"""
        with pytest.raises(ValueError, match="Invalid owner_id"):
            await MerchantService.get_merchant_hotels("")

        with pytest.raises(ValueError, match="Invalid owner_id"):
            await MerchantService.get_merchant_hotels(None)

    @pytest.mark.anyio
    async def test_update_hotel_details(self, setup_merchant_with_hotel):
        """Test updating hotel details by merchant"""
        hotel = setup_merchant_with_hotel["hotel"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        update_data = {
            "name": "Updated Merchant Hotel",
            "address": "New Address 123",
            "phone_number": "09876543210"
        }

        updated_hotel = await MerchantService.update_hotel_details(
            owner_id,
            str(hotel.id),
            update_data
        )

        assert updated_hotel.name == "Updated Merchant Hotel"
        assert updated_hotel.address == "New Address 123"

    @pytest.mark.anyio
    async def test_update_hotel_details_not_owner(self, setup_merchant_with_hotel):
        """Test that non-owner cannot update hotel"""
        hotel = setup_merchant_with_hotel["hotel"]

        update_data = {"name": "Unauthorized Update"}

        with pytest.raises(ValueError, match="Not authorized"):
            await MerchantService.update_hotel_details(
                "different_owner",
                str(hotel.id),
                update_data
            )

    @pytest.mark.anyio
    async def test_set_hotel_availability_close(self, setup_merchant_with_hotel):
        """Test closing a hotel for business"""
        hotel = setup_merchant_with_hotel["hotel"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        updated_hotel = await MerchantService.set_hotel_availability(
            owner_id,
            str(hotel.id),
            False
        )

        assert updated_hotel.is_open is False

    @pytest.mark.anyio
    async def test_set_hotel_availability_open(self, setup_merchant_with_hotel):
        """Test opening a hotel for business"""
        hotel = setup_merchant_with_hotel["hotel"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        # First close it
        await MerchantService.set_hotel_availability(owner_id, str(hotel.id), False)

        # Then open it
        updated_hotel = await MerchantService.set_hotel_availability(
            owner_id,
            str(hotel.id),
            True
        )

        assert updated_hotel.is_open is True

    @pytest.mark.anyio
    async def test_set_hotel_availability_not_owner(self, setup_merchant_with_hotel):
        """Test that non-owner cannot change hotel availability"""
        hotel = setup_merchant_with_hotel["hotel"]

        with pytest.raises(ValueError, match="Not authorized"):
            await MerchantService.set_hotel_availability(
                "different_owner",
                str(hotel.id),
                False
            )

    @pytest.mark.anyio
    async def test_get_merchant_hotel_suites(self, setup_merchant_with_hotel):
        """Test getting all suites for a merchant's hotel"""
        hotel = setup_merchant_with_hotel["hotel"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        suites = await MerchantService.get_merchant_hotel_suites(
            owner_id,
            str(hotel.id)
        )

        assert isinstance(suites, list)
        assert len(suites) == 3  # We created 3 suites

    @pytest.mark.anyio
    async def test_get_merchant_hotel_suites_not_owner(self, setup_merchant_with_hotel):
        """Test that non-owner cannot view hotel suites through merchant service"""
        hotel = setup_merchant_with_hotel["hotel"]

        with pytest.raises(ValueError, match="Not authorized"):
            await MerchantService.get_merchant_hotel_suites(
                "different_owner",
                str(hotel.id)
            )

    @pytest.mark.anyio
    async def test_get_merchant_bookings(self, setup_merchant_with_hotel):
        """Test getting all bookings for a merchant's hotels"""
        hotel = setup_merchant_with_hotel["hotel"]
        suites = setup_merchant_with_hotel["suites"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        # Create a booking
        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suites[0].id),
            "guest_name": "Merchant Booking Guest",
            "guest_phone": "08011112222",
            "check_in_date": datetime.now() + timedelta(days=5),
            "check_out_date": datetime.now() + timedelta(days=7),
            "total_amount": Money("200.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)

        merchant_bookings = await MerchantService.get_merchant_bookings(owner_id)

        assert isinstance(merchant_bookings, list)
        assert len(merchant_bookings) >= 1

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_get_merchant_bookings_by_hotel(self, setup_merchant_with_hotel):
        """Test getting bookings for a specific hotel"""
        hotel = setup_merchant_with_hotel["hotel"]
        suites = setup_merchant_with_hotel["suites"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        # Create a booking
        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suites[1].id),
            "guest_name": "Hotel Specific Guest",
            "guest_phone": "08033334444",
            "check_in_date": datetime.now() + timedelta(days=10),
            "check_out_date": datetime.now() + timedelta(days=12),
            "total_amount": Money("150.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)

        hotel_bookings = await MerchantService.get_merchant_bookings_by_hotel(
            owner_id,
            str(hotel.id)
        )

        assert isinstance(hotel_bookings, list)
        assert len(hotel_bookings) >= 1
        assert all(b.hotel_id == str(hotel.id) for b in hotel_bookings)

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_get_merchant_revenue_summary(self, setup_merchant_with_hotel):
        """Test getting revenue summary for a merchant"""
        hotel = setup_merchant_with_hotel["hotel"]
        suites = setup_merchant_with_hotel["suites"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        # Create completed bookings for revenue calculation
        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suites[0].id),
            "guest_name": "Revenue Test Guest",
            "guest_phone": "08055556666",
            "check_in_date": datetime.now() - timedelta(days=5),
            "check_out_date": datetime.now() - timedelta(days=3),
            "total_amount": Money("300.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)
        booking.status = BookingStatus.COMPLETED
        await booking.save()

        summary = await MerchantService.get_merchant_revenue_summary(owner_id)

        assert "total_bookings" in summary
        assert "total_revenue" in summary
        assert "completed_bookings" in summary
        assert isinstance(summary["total_bookings"], int)

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_set_suite_availability(self, setup_merchant_with_hotel):
        """Test setting suite availability by merchant"""
        hotel = setup_merchant_with_hotel["hotel"]
        suites = setup_merchant_with_hotel["suites"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        # Make suite unavailable
        updated_suite = await MerchantService.set_suite_availability(
            owner_id,
            str(hotel.id),
            str(suites[0].id),
            False
        )

        assert updated_suite.is_available is False

        # Make it available again
        updated_suite = await MerchantService.set_suite_availability(
            owner_id,
            str(hotel.id),
            str(suites[0].id),
            True
        )

        assert updated_suite.is_available is True

    @pytest.mark.anyio
    async def test_set_suite_availability_not_owner(self, setup_merchant_with_hotel):
        """Test that non-owner cannot change suite availability"""
        hotel = setup_merchant_with_hotel["hotel"]
        suites = setup_merchant_with_hotel["suites"]

        with pytest.raises(ValueError, match="Not authorized"):
            await MerchantService.set_suite_availability(
                "different_owner",
                str(hotel.id),
                str(suites[0].id),
                False
            )

    @pytest.mark.anyio
    async def test_get_hotel_dashboard_stats(self, setup_merchant_with_hotel):
        """Test getting dashboard statistics for a hotel"""
        hotel = setup_merchant_with_hotel["hotel"]
        owner_id = setup_merchant_with_hotel["owner_id"]

        stats = await MerchantService.get_hotel_dashboard_stats(
            owner_id,
            str(hotel.id)
        )

        assert "total_suites" in stats
        assert "available_suites" in stats
        assert "unavailable_suites" in stats
        assert "total_bookings" in stats
        assert "pending_bookings" in stats
        assert "checked_in_guests" in stats
        assert stats["total_suites"] == 3  # We created 3 suites

