"""Tests for Booking Repository - Following TDD approach"""

import pytest
from datetime import datetime, timedelta

from app.repositories.booking import BookingRepository
from app.repositories.hotel import HotelRepository
from app.models.hotel import Hotel, HotelSuite
from app.models.booking import Booking, BookingType, BookingStatus
from app.models.money import Money


@pytest.fixture
async def setup_hotel_with_suite():
    """Setup a hotel with a suite for booking tests"""
    hotel_data = {
        "name": "Booking Test Hotel",
        "address": "123 Test Street",
        "email_address": "booking@testhotel.com",
        "phone_number": "1234567890",
        "state": "Test State",
        "country": "Test Country",
        "lga": "Test LGA",
        "registration_type": "CAC",
        "registration_image_link": "http://example.com/image.jpg",
        "owner_id": "merchant_owner_123",
        "is_approved": True,
        "is_open": True
    }
    hotel = await HotelRepository.create_hotel(Hotel(**hotel_data))

    suite_data = {
        "hotel_id": str(hotel.id),
        "name": "Deluxe Suite",
        "price": Money("150.00"),
        "description": "A luxurious deluxe suite",
        "room_number": 101,
        "facilities": ["WiFi", "TV", "Air Conditioning"],
        "is_available": True
    }
    suite = await HotelRepository.create_hotel_suite(HotelSuite(**suite_data))

    yield {"hotel": hotel, "suite": suite}

    # Cleanup
    await suite.delete()
    await hotel.delete()


@pytest.fixture
async def setup_booking(setup_hotel_with_suite):
    """Setup a booking for tests that need an existing booking"""
    hotel = setup_hotel_with_suite["hotel"]
    suite = setup_hotel_with_suite["suite"]

    booking_data = {
        "hotel_id": str(hotel.id),
        "suite_id": str(suite.id),
        "guest_name": "John Doe",
        "guest_phone": "08012345678",
        "guest_email": "john.doe@example.com",
        "check_in_date": datetime.now() + timedelta(days=1),
        "check_out_date": datetime.now() + timedelta(days=3),
        "booking_type": BookingType.ONLINE,
        "status": BookingStatus.CONFIRMED,
        "total_amount": Money("300.00"),
        "number_of_guests": 2
    }
    booking = await BookingRepository.create_booking(Booking(**booking_data))

    yield {"booking": booking, "hotel": hotel, "suite": suite}

    # Cleanup
    try:
        await booking.delete()
    except Exception:
        pass  # Booking may have been deleted in test


class TestBookingRepository:

    @pytest.mark.anyio
    async def test_create_booking(self, setup_hotel_with_suite):
        """Test creating a new booking"""
        hotel = setup_hotel_with_suite["hotel"]
        suite = setup_hotel_with_suite["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Jane Smith",
            "guest_phone": "08098765432",
            "guest_email": "jane.smith@example.com",
            "check_in_date": datetime.now() + timedelta(days=5),
            "check_out_date": datetime.now() + timedelta(days=7),
            "booking_type": BookingType.ONLINE,
            "status": BookingStatus.PENDING,
            "total_amount": Money("300.00"),
            "number_of_guests": 1
        }

        booking = await BookingRepository.create_booking(Booking(**booking_data))

        assert booking.id is not None
        assert booking.hotel_id == str(hotel.id)
        assert booking.suite_id == str(suite.id)
        assert booking.guest_name == "Jane Smith"
        assert booking.status == BookingStatus.PENDING
        assert booking.total_amount == Money("300.00")

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_create_walk_in_booking(self, setup_hotel_with_suite):
        """Test creating a walk-in booking by merchant"""
        hotel = setup_hotel_with_suite["hotel"]
        suite = setup_hotel_with_suite["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Walk-in Guest",
            "guest_phone": "08011111111",
            "check_in_date": datetime.now(),
            "check_out_date": datetime.now() + timedelta(days=1),
            "booking_type": BookingType.WALK_IN,
            "status": BookingStatus.CHECKED_IN,
            "total_amount": Money("150.00"),
            "booked_by_owner_id": "merchant_owner_123",
            "number_of_guests": 1
        }

        booking = await BookingRepository.create_booking(Booking(**booking_data))

        assert booking.booking_type == BookingType.WALK_IN
        assert booking.booked_by_owner_id == "merchant_owner_123"
        assert booking.status == BookingStatus.CHECKED_IN

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_get_booking_by_id(self, setup_booking):
        """Test retrieving a booking by its ID"""
        original_booking = setup_booking["booking"]

        fetched_booking = await BookingRepository.get_booking_by_id(str(original_booking.id))

        assert fetched_booking is not None
        assert fetched_booking.id == original_booking.id
        assert fetched_booking.guest_name == original_booking.guest_name

    @pytest.mark.anyio
    async def test_get_booking_by_id_not_found(self):
        """Test getting a booking that doesn't exist"""
        result = await BookingRepository.get_booking_by_id("000000000000000000000000")
        assert result is None

    @pytest.mark.anyio
    async def test_get_bookings_by_hotel_id(self, setup_booking):
        """Test getting all bookings for a specific hotel"""
        hotel = setup_booking["hotel"]

        bookings = await BookingRepository.get_bookings_by_hotel_id(str(hotel.id))

        assert isinstance(bookings, list)
        assert len(bookings) >= 1
        assert all(b.hotel_id == str(hotel.id) for b in bookings)

    @pytest.mark.anyio
    async def test_get_bookings_by_suite_id(self, setup_booking):
        """Test getting all bookings for a specific suite"""
        suite = setup_booking["suite"]

        bookings = await BookingRepository.get_bookings_by_suite_id(str(suite.id))

        assert isinstance(bookings, list)
        assert len(bookings) >= 1
        assert all(b.suite_id == str(suite.id) for b in bookings)

    @pytest.mark.anyio
    async def test_get_bookings_by_owner_id(self, setup_hotel_with_suite):
        """Test getting all bookings for hotels owned by a specific merchant"""
        hotel = setup_hotel_with_suite["hotel"]
        suite = setup_hotel_with_suite["suite"]
        owner_id = hotel.owner_id

        # Create a walk-in booking
        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "Owner Created Guest",
            "guest_phone": "08022222222",
            "check_in_date": datetime.now(),
            "check_out_date": datetime.now() + timedelta(days=1),
            "booking_type": BookingType.WALK_IN,
            "status": BookingStatus.CONFIRMED,
            "total_amount": Money("150.00"),
            "booked_by_owner_id": owner_id,
            "number_of_guests": 1
        }
        booking = await BookingRepository.create_booking(Booking(**booking_data))

        bookings = await BookingRepository.get_bookings_by_owner_id(owner_id)

        assert isinstance(bookings, list)
        assert len(bookings) >= 1

        # Cleanup
        await booking.delete()

    @pytest.mark.anyio
    async def test_update_booking_status(self, setup_booking):
        """Test updating a booking's status"""
        booking = setup_booking["booking"]

        updated_booking = await BookingRepository.update_booking_status(
            str(booking.id),
            BookingStatus.CHECKED_IN
        )

        assert updated_booking.status == BookingStatus.CHECKED_IN

    @pytest.mark.anyio
    async def test_update_booking_status_not_found(self):
        """Test updating status of non-existent booking"""
        with pytest.raises(ValueError, match="Booking not found"):
            await BookingRepository.update_booking_status(
                "000000000000000000000000",
                BookingStatus.CANCELLED
            )

    @pytest.mark.anyio
    async def test_get_bookings_by_date_range(self, setup_booking):
        """Test getting bookings within a date range"""
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=10)

        bookings = await BookingRepository.get_bookings_by_date_range(start_date, end_date)

        assert isinstance(bookings, list)

    @pytest.mark.anyio
    async def test_delete_booking(self, setup_hotel_with_suite):
        """Test deleting a booking"""
        hotel = setup_hotel_with_suite["hotel"]
        suite = setup_hotel_with_suite["suite"]

        booking_data = {
            "hotel_id": str(hotel.id),
            "suite_id": str(suite.id),
            "guest_name": "To Delete",
            "guest_phone": "08033333333",
            "check_in_date": datetime.now() + timedelta(days=10),
            "check_out_date": datetime.now() + timedelta(days=12),
            "booking_type": BookingType.ONLINE,
            "status": BookingStatus.PENDING,
            "total_amount": Money("300.00"),
            "number_of_guests": 1
        }
        booking = await BookingRepository.create_booking(Booking(**booking_data))
        booking_id = str(booking.id)

        deleted_booking = await BookingRepository.delete_booking(booking_id)

        assert deleted_booking.id == booking.id

        # Verify it's deleted
        result = await BookingRepository.get_booking_by_id(booking_id)
        assert result is None

    @pytest.mark.anyio
    async def test_delete_booking_not_found(self):
        """Test deleting a non-existent booking"""
        with pytest.raises(ValueError, match="Booking not found"):
            await BookingRepository.delete_booking("000000000000000000000000")

    @pytest.mark.anyio
    async def test_get_bookings_by_status(self, setup_booking):
        """Test getting bookings by status"""
        hotel = setup_booking["hotel"]

        bookings = await BookingRepository.get_bookings_by_status(
            str(hotel.id),
            BookingStatus.CONFIRMED
        )

        assert isinstance(bookings, list)
        assert all(b.status == BookingStatus.CONFIRMED for b in bookings)

    @pytest.mark.anyio
    async def test_check_suite_availability(self, setup_booking):
        """Test checking if a suite is available for given dates"""
        suite = setup_booking["suite"]
        booking = setup_booking["booking"]

        # Check for overlapping dates (should be unavailable)
        check_in = booking.check_in_date
        check_out = booking.check_out_date

        is_available = await BookingRepository.check_suite_availability(
            str(suite.id),
            check_in,
            check_out
        )

        assert is_available is False

    @pytest.mark.anyio
    async def test_check_suite_availability_no_conflict(self, setup_booking):
        """Test that suite is available for non-overlapping dates"""
        suite = setup_booking["suite"]
        booking = setup_booking["booking"]

        # Check for dates after the existing booking
        check_in = booking.check_out_date + timedelta(days=5)
        check_out = booking.check_out_date + timedelta(days=7)

        is_available = await BookingRepository.check_suite_availability(
            str(suite.id),
            check_in,
            check_out
        )

        assert is_available is True

