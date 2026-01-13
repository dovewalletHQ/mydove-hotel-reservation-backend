"""Tests for Booking Service - Following TDD approach"""

import pytest
from datetime import datetime, timedelta

from app.services.booking import BookingService
from app.repositories.hotel import HotelRepository
from app.models.hotel import Hotel, HotelSuite
from app.models.booking import Booking, BookingType, BookingStatus
from app.models.money import Money


@pytest.fixture
async def setup_merchant_hotel():
    """Setup a hotel with suites for merchant booking tests"""
    hotel_data = {
        "name": "Merchant Test Hotel",
        "address": "123 Merchant Street",
        "email_address": "merchant@testhotel.com",
        "phone_number": "1234567890",
        "state": "Test State",
        "country": "Test Country",
        "lga": "Test LGA",
        "registration_type": "CAC",
        "registration_image_link": "http://example.com/image.jpg",
        "owner_id": "merchant_001",
        "is_approved": True,
        "is_open": True
    }
    hotel = await HotelRepository.create_hotel(Hotel(**hotel_data))

    suite_data = {
        "hotel_id": str(hotel.id),
        "name": "Standard Room",
        "price": Money("100.00"),
        "description": "A comfortable standard room",
        "room_number": 201,
        "facilities": ["WiFi", "TV"],
        "is_available": True
    }
    suite = await HotelRepository.create_hotel_suite(HotelSuite(**suite_data))

    yield {"hotel": hotel, "suite": suite, "owner_id": "merchant_001"}

    # Cleanup
    await suite.delete()
    await hotel.delete()


class TestBookingService:

    @pytest.mark.anyio
    async def test_create_booking_success(self, setup_merchant_hotel):
        """Test creating a booking successfully"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Alice Johnson",
            "guest_phone": "08045678901",
            "guest_email": "alice@example.com",
            "check_in_date": datetime.now() + timedelta(days=5),
            "check_out_date": datetime.now() + timedelta(days=7),
            "total_amount": Money("200.00"),
            "number_of_guests": 2
        }

        booking = await BookingService.create_booking(booking_data)

        assert booking.id is not None
        assert booking.guest_name == "Alice Johnson"
        assert booking.status == BookingStatus.PENDING
        assert booking.booking_type == BookingType.ONLINE

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_create_booking_hotel_not_found(self, setup_merchant_hotel):
        """Test creating booking for non-existent hotel"""
        suite = setup_merchant_hotel["suite"]

        booking_data = {
            "hotel_id": "000000000000000000000000",
            "suite_id": str(suite.id),
            "guest_name": "Bob Smith",
            "guest_phone": "08012345678",
            "check_in_date": datetime.now() + timedelta(days=1),
            "check_out_date": datetime.now() + timedelta(days=2),
            "total_amount": Money("100.00"),
            "number_of_guests": 1
        }

        with pytest.raises(ValueError, match="Hotel not found"):
            await BookingService.create_booking(booking_data)

    @pytest.mark.anyio
    async def test_create_booking_hotel_closed(self, setup_merchant_hotel):
        """Test creating booking for closed hotel"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        # Close the hotel
        await HotelRepository.toggle_hotel_availability(str(hotel.id), False)

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Carol White",
            "guest_phone": "08098765432",
            "check_in_date": datetime.now() + timedelta(days=1),
            "check_out_date": datetime.now() + timedelta(days=2),
            "total_amount": Money("100.00"),
            "number_of_guests": 1
        }

        with pytest.raises(ValueError, match="Hotel is currently closed"):
            await BookingService.create_booking(booking_data)

        # Reopen hotel for other tests
        await HotelRepository.toggle_hotel_availability(str(hotel.id), True)

    @pytest.mark.anyio
    async def test_create_booking_suite_unavailable(self, setup_merchant_hotel):
        """Test creating booking for unavailable suite"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        # Mark suite as unavailable
        suite.is_available = False
        await suite.save()

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Dave Brown",
            "guest_phone": "08011112222",
            "check_in_date": datetime.now() + timedelta(days=1),
            "check_out_date": datetime.now() + timedelta(days=2),
            "total_amount": Money("100.00"),
            "number_of_guests": 1
        }

        with pytest.raises(ValueError, match="Suite is not available"):
            await BookingService.create_booking(booking_data)

        # Restore suite availability
        suite.is_available = True
        await suite.save()

    @pytest.mark.anyio
    async def test_create_booking_date_conflict(self, setup_merchant_hotel):
        """Test creating booking with conflicting dates"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        # Create first booking
        first_booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "First Guest",
            "guest_phone": "08033334444",
            "check_in_date": datetime.now() + timedelta(days=10),
            "check_out_date": datetime.now() + timedelta(days=15),
            "total_amount": Money("500.00"),
            "number_of_guests": 1
        }
        first_booking = await BookingService.create_booking(first_booking_data)

        # Try to create overlapping booking
        second_booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Second Guest",
            "guest_phone": "08055556666",
            "check_in_date": datetime.now() + timedelta(days=12),  # Overlaps!
            "check_out_date": datetime.now() + timedelta(days=17),
            "total_amount": Money("500.00"),
            "number_of_guests": 1
        }

        with pytest.raises(ValueError, match="Suite is not available for the selected dates"):
            await BookingService.create_booking(second_booking_data)

        # Cleanup
        await first_booking.delete()

    @pytest.mark.anyio
    async def test_create_walk_in_booking(self, setup_merchant_hotel):
        """Test creating a walk-in booking by merchant"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]
        owner_id = setup_merchant_hotel["owner_id"]

        walk_in_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Walk-in Customer",
            "guest_phone": "08077778888",
            "check_in_date": datetime.now(),
            "check_out_date": datetime.now() + timedelta(days=1),
            "total_amount": Money("100.00"),
            "number_of_guests": 1,
            "special_requests": "Late checkout"
        }

        booking = await BookingService.create_walk_in_booking(owner_id, walk_in_data)

        assert booking.booking_type == BookingType.WALK_IN
        assert booking.booked_by_owner_id == owner_id
        assert booking.status == BookingStatus.CHECKED_IN

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_create_walk_in_booking_not_owner(self, setup_merchant_hotel):
        """Test that non-owner cannot create walk-in booking"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        walk_in_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Invalid Walk-in",
            "guest_phone": "08099990000",
            "check_in_date": datetime.now(),
            "check_out_date": datetime.now() + timedelta(days=1),
            "total_amount": Money("100.00"),
            "number_of_guests": 1
        }

        with pytest.raises(ValueError, match="Not authorized"):
            await BookingService.create_walk_in_booking("different_owner", walk_in_data)

    @pytest.mark.anyio
    async def test_get_booking_details(self, setup_merchant_hotel):
        """Test getting booking details"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Eve Green",
            "guest_phone": "08011223344",
            "check_in_date": datetime.now() + timedelta(days=20),
            "check_out_date": datetime.now() + timedelta(days=22),
            "total_amount": Money("200.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)

        details = await BookingService.get_booking_details(str(booking.id))

        assert details is not None
        assert details.guest_name == "Eve Green"

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_get_booking_details_not_found(self):
        """Test getting non-existent booking details"""
        with pytest.raises(ValueError, match="Booking not found"):
            await BookingService.get_booking_details("000000000000000000000000")

    @pytest.mark.anyio
    async def test_cancel_booking(self, setup_merchant_hotel):
        """Test cancelling a booking"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Cancel Test",
            "guest_phone": "08055667788",
            "check_in_date": datetime.now() + timedelta(days=30),
            "check_out_date": datetime.now() + timedelta(days=32),
            "total_amount": Money("200.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)

        cancelled_booking = await BookingService.cancel_booking(str(booking.id))

        assert cancelled_booking.status == BookingStatus.CANCELLED

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_get_booked_rooms_by_hotel(self, setup_merchant_hotel):
        """Test getting all booked rooms for a hotel"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        # Create a booking
        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Booked Room Test",
            "guest_phone": "08099887766",
            "check_in_date": datetime.now() + timedelta(days=40),
            "check_out_date": datetime.now() + timedelta(days=42),
            "total_amount": Money("200.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)

        booked_rooms = await BookingService.get_booked_rooms_by_hotel(str(hotel.id))

        assert isinstance(booked_rooms, list)
        assert len(booked_rooms) >= 1

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_get_bookings_for_merchant(self, setup_merchant_hotel):
        """Test getting all bookings for a merchant's hotels"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]
        owner_id = setup_merchant_hotel["owner_id"]

        # Create a walk-in booking
        walk_in_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Merchant Booking Test",
            "guest_phone": "08011122233",
            "check_in_date": datetime.now() + timedelta(days=50),
            "check_out_date": datetime.now() + timedelta(days=52),
            "total_amount": Money("200.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_walk_in_booking(owner_id, walk_in_data)

        merchant_bookings = await BookingService.get_bookings_for_merchant(owner_id)

        assert isinstance(merchant_bookings, list)
        assert len(merchant_bookings) >= 1

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_check_in_guest(self, setup_merchant_hotel):
        """Test checking in a guest"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Check-in Test",
            "guest_phone": "08044455566",
            "check_in_date": datetime.now(),
            "check_out_date": datetime.now() + timedelta(days=2),
            "total_amount": Money("200.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)

        # Confirm the booking first
        await BookingService.confirm_booking(str(booking.id))

        checked_in = await BookingService.check_in_guest(str(booking.id))

        assert checked_in.status == BookingStatus.CHECKED_IN

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_check_out_guest(self, setup_merchant_hotel):
        """Test checking out a guest"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Check-out Test",
            "guest_phone": "08077788899",
            "check_in_date": datetime.now() - timedelta(days=2),
            "check_out_date": datetime.now(),
            "total_amount": Money("200.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)

        # Set status to checked in
        booking.status = BookingStatus.CHECKED_IN
        await booking.save()

        checked_out = await BookingService.check_out_guest(str(booking.id))

        assert checked_out.status == BookingStatus.CHECKED_OUT

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_confirm_booking(self, setup_merchant_hotel):
        """Test confirming a pending booking"""
        hotel = setup_merchant_hotel["hotel"]
        suite = setup_merchant_hotel["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Confirm Test",
            "guest_phone": "08000011122",
            "check_in_date": datetime.now() + timedelta(days=60),
            "check_out_date": datetime.now() + timedelta(days=62),
            "total_amount": Money("200.00"),
            "number_of_guests": 1
        }
        booking = await BookingService.create_booking(booking_data)

        assert booking.status == BookingStatus.PENDING

        confirmed = await BookingService.confirm_booking(str(booking.id))

        assert confirmed.status == BookingStatus.CONFIRMED

        # Cleanup
        await booking.delete()

