from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.models.booking import HotelSuiteBookingRequest, UserBookings
from app.models.hotel import HotelSuite
from app.models.money import Money
from app.services.booking import BookingService
from app.services.hotel_suites import HotelSuiteService
from app.core.logger import logger
from app.utils.response import create_response

router = APIRouter()


class HotelSuiteCreateRequest(BaseModel):
    hotel_id: str = Field(...)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="NGN", min_length=3, max_length=3)
    capacity: int = Field(default=2, ge=1)
    facilities: Optional[List[str]] = None
    images: Optional[List[str]] = None


class HotelSuiteUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    capacity: Optional[int] = Field(None, ge=1)
    facilities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    is_available: Optional[bool] = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_hotel_suite(request: HotelSuiteCreateRequest):
    """Create a new hotel suite."""
    try:
        data = request.model_dump()
        # Convert price to Money type
        data["price"] = Money(data.pop("price"))
        suite = await HotelSuiteService.create_hotel_suite(HotelSuite(**data))
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Hotel suite created successfully",
            data=suite,
        )
    except ValueError as e:
        logger.warning("Failed to create hotel suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error creating hotel suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("")
async def get_all_suites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_available: Optional[bool] = None,
    price: Optional[float] = None,
):
    """Get all hotel suites with optional filtering."""
    try:
        suites = await HotelSuiteService.get_all_hotel_suites()
        if is_available is not None:
            suites = [s for s in suites if s.is_available == is_available]
        if price is not None:
            suites = [s for s in suites if s.price <= price]
        return create_response(
            status_code=status.HTTP_200_OK,
            message="All suites retrieved successfully",
            data=suites[skip : skip + limit]
        )
    except ValueError as e:
        logger.warning("Failed to get all suites: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error fetching suites: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("/{suite_id}")
async def get_suite_by_id(suite_id: str):
    """Get a hotel suite by ID."""
    try:
        suite = await HotelSuiteService.get_hotel_suite_by_id(suite_id)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Suite retrieved successfully",
            data=suite
        )
    except ValueError as e:
        logger.warning("Failed to get suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Invalid suite ID",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=str(e)
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("/hotel/{hotel_id}")
async def get_suites_by_hotel(hotel_id: str, is_available: Optional[bool] = None):
    """Get all suites for a specific hotel."""
    try:
        suites = await HotelSuiteService.get_hotel_suites_by_hotel_id(hotel_id)
        if is_available is not None:
            suites = [s for s in suites if s.is_available == is_available]
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Suites retrieved successfully",
            data=suites
        )
    except Exception as e:
        logger.error("Unexpected error fetching suites by hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.patch("/{suite_id}")
async def update_suite(suite_id: str, request: HotelSuiteUpdateRequest):
    """Update a hotel suite."""
    try:
        update_data = request.model_dump(exclude_unset=True)
        # Handle price/currency updates
        if "price" in update_data or "currency" in update_data:
            # Get existing suite to preserve currency if only price is updated
            existing_suite = await HotelSuiteService.get_hotel_suite_by_id(suite_id)
            if not existing_suite:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")

            price = update_data.pop("price", existing_suite.price)
            currency = update_data.pop("currency", existing_suite.currency)
            update_data["price"] = Money(price)
            update_data['currency'] = currency

        suite = await HotelSuiteService.update_hotel_suite(suite_id, update_data)
        if not suite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Suite updated successfully",
            data=suite
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Failed to update suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Failed to update suite, error: {}".format(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error updating suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.delete("/{suite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_suite(suite_id: str):
    """Delete a hotel suite."""
    try:
        result = await HotelSuiteService.delete_suite(suite_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")
        return create_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Suite deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error deleting suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.patch("/{suite_id}/availability", response_model=HotelSuite)
async def toggle_suite_availability(suite_id: str, is_available: bool):
    """Toggle suite availability."""
    try:
        suite = await HotelSuiteService.update_suite(suite_id, {"is_available": is_available})
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Suite availability toggled successfully",
            data=suite
        )
    except ValueError as e:
        logger.warning("Failed to toggle suite availability: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error toggling suite availability: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.post("/users/bookings")
async def book_suite(req: HotelSuiteBookingRequest):
    """Book a hotel suite."""
    try:
        suite = await HotelSuiteService.book_suite(req.suite_id, req)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Suite booked successfully",
            data=suite
        )
    except ValueError as e:
        logger.error("Error booking suite with id '%s': %s", req.suite_id[:7], e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error booking suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("/user/bookings")
async def get_booked_suites_by_user(req: UserBookings ):
    """Get all booked suites for a specific user by guest phone number."""
    try:
        bookings = await BookingService.get_bookings_by_guest_phone(req.guest_phone)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Booked suites retrieved successfully",
            data=bookings
        )
    except ValueError as e:
        logger.warning("Failed to get booked suites: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error fetching booked suites: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)