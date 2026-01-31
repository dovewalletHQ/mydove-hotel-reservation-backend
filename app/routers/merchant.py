"""Merchant Router - API endpoints for merchant/owner operations"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.hotel import Hotel, HotelSuite
from app.models.booking import Booking
from app.services.merchant import MerchantService
from app.core.logger import logger
from app.utils.response import create_response

router = APIRouter()


# ====================
# Request/Response Models
# ====================

class HotelCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    lga: Optional[str] = None
    registration_type: str = Field(default="CAC")
    registration_image_link: Optional[str] = None


class HotelUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    lga: Optional[str] = None


class HotelAvailabilityRequest(BaseModel):
    is_open: bool


class SuiteCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    room_number: int = Field(..., ge=1)
    room_type: Optional[str] = None
    facilities: List[str] = Field(default_factory=list)
    suite_photo_urls: List[str] = Field(default_factory=list)
    is_available: bool = True


class SuiteUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    room_number: Optional[int] = Field(None, ge=1)
    room_type: Optional[str] = None
    facilities: Optional[List[str]] = None
    suite_photo_urls: Optional[List[str]] = None
    is_available: Optional[bool] = None


class SuiteAvailabilityRequest(BaseModel):
    is_available: bool


# ====================
# Hotel Management Endpoints
# ====================

@router.get("/{owner_id}/hotels")
async def get_merchant_hotels(owner_id: str):
    """Get all hotels owned by a merchant"""
    try:
        hotels = await MerchantService.get_merchant_hotels(owner_id)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="list of owned hotels",
            data=hotels
        )
    except ValueError as e:
        logger.warning("Failed to get merchant hotels: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error getting merchant hotels: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.post("/{owner_id}/hotels", status_code=status.HTTP_201_CREATED)
async def create_hotel(owner_id: str, request: HotelCreateRequest):
    """Create a new hotel for a merchant"""
    try:
        hotel = await MerchantService.create_hotel(owner_id, request.model_dump())
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="New hotel added, waiting for admin approval",
            data=hotel.model_dump()
        )
    except ValueError as e:
        logger.warning("Failed to create hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Failed to create hotel, error: {}".format(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error creating hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.patch("/{owner_id}/hotels/{hotel_id}")
async def update_hotel(owner_id: str, hotel_id: str, request: HotelUpdateRequest):
    """Update a hotel owned by a merchant"""
    try:
        update_data = request.model_dump(exclude_unset=True)
        hotel = await MerchantService.update_hotel_details(owner_id, hotel_id, update_data)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="hotel updated successfully",
            data=hotel.model_dump()
        )
    except ValueError as e:
        logger.warning("Failed to update hotel: %s", e)
        if "not found" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="hotel with id not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        if "not authorized" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Opps! seems like you are not authorized to take this action for this hotel"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_response)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong while updating hotel details",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error updating hotel: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{owner_id}/hotels/{hotel_id}/availability")
async def set_hotel_availability(owner_id: str, hotel_id: str, request: HotelAvailabilityRequest):
    """Set hotel availability (open/closed for business)"""
    try:
        hotel = await MerchantService.set_hotel_availability(owner_id, hotel_id, request.is_open)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="hotel availability updated successfully",
            data=hotel.model_dump()
        )
    except ValueError as e:
        logger.warning("Failed to set hotel availability: %s", e)
        if "not found" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="hotel with id not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        if "not authorized" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Opps! seems like you are not authorized to take this action for this hotel"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_response)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Something went wrong while setting hotel availability",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error setting hotel availability: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


# ====================
# Suite Management Endpoints
# ====================

@router.get("/{owner_id}/hotels/{hotel_id}/suites", response_model=List[HotelSuite])
async def get_merchant_hotel_suites(owner_id: str, hotel_id: str):
    """Get all suites for a merchant's hotel"""
    try:
        suites = await MerchantService.get_merchant_hotel_suites(owner_id, hotel_id)
        return suites
    except ValueError as e:
        logger.warning("Failed to get hotel suites: %s", e)
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error getting hotel suites: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/{owner_id}/hotels/{hotel_id}/suites")
async def create_suite(owner_id: str, hotel_id: str, request: SuiteCreateRequest):
    """Create a new suite for a merchant's hotel"""
    try:
        suite_data = request.model_dump()
        suite = await MerchantService.create_suite(owner_id, hotel_id, suite_data)
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="suite created successfully",
            data=suite
        )
    except ValueError as e:
        logger.warning("Failed to create suite: %s", e)
        if "not found" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="hotel with id not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        if "not authorized" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Opps! seems like you are not authorized to take this action for this hotel"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_response)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error creating suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.patch("/{owner_id}/hotels/{hotel_id}/suites/{suite_id}", response_model=HotelSuite)
async def update_suite(owner_id: str, hotel_id: str, suite_id: str, request: SuiteUpdateRequest):
    """Update a suite in a merchant's hotel"""
    try:
        update_data = request.model_dump(exclude_unset=True)
        suite = await MerchantService.update_suite(owner_id, hotel_id, suite_id, update_data)
        return suite
    except ValueError as e:
        logger.warning("Failed to update suite: %s", e)
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "not authorized" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error updating suite: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{owner_id}/hotels/{hotel_id}/suites/{suite_id}", response_model=HotelSuite)
async def delete_suite(owner_id: str, hotel_id: str, suite_id: str):
    """Delete a suite from a merchant's hotel"""
    try:
        suite = await MerchantService.delete_suite(owner_id, hotel_id, suite_id)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="suite deleted successfully",
            data=suite
        )
    except ValueError as e:
        logger.warning("Failed to delete suite: %s", e)
        if "not found" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="hotel with id not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        if "not authorized" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Opps! seems like you are not authorized to take this action for this hotel"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_response)
        if "active bookings" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_409_CONFLICT,
                message="Opps! seems like you are not authorized to take this action for this hotel"
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error_response)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Failed to delete suite, error: {}".format(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error deleting suite: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.patch("/{owner_id}/hotels/{hotel_id}/suites/{suite_id}/availability", response_model=HotelSuite)
async def set_suite_availability(
    owner_id: str,
    hotel_id: str,
    suite_id: str,
    request: SuiteAvailabilityRequest
):
    """Set suite availability (available/unavailable)"""
    try:
        suite = await MerchantService.set_suite_availability(
            owner_id, hotel_id, suite_id, request.is_available
        )
        return create_response(
            status_code=status.HTTP_200_OK,
            message="suite availability updated successfully",
            data=suite.model_dump()
        )
    except ValueError as e:
        logger.warning("Failed to set suite availability: %s", e)
        if "not found" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="suite or hotel not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        if "not authorized" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Opps! seems like you are not authorized to take this action for this suite"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_response)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Failed to set suite availability, error: {}".format(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error setting suite availability: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


# ====================
# Booking Management Endpoints
# ====================

@router.get("/{owner_id}/bookings")
async def get_merchant_bookings(owner_id: str):
    """Get all bookings for all hotels owned by a merchant"""
    try:
        bookings = await MerchantService.get_merchant_bookings(owner_id)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="merchant bookings retrieved successfully",
            data=bookings
        )
    except ValueError as e:
        logger.warning("Failed to get merchant bookings: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Failed to get merchant bookings, error: {}".format(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error getting merchant bookings: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)

@router.get("/{owner_id}/hotels/{hotel_id}/bookings")
async def get_merchant_hotel_bookings(owner_id: str, hotel_id: str):
    """Get all bookings for a specific hotel owned by a merchant"""
    try:
        bookings = await MerchantService.get_merchant_bookings_by_hotel(owner_id, hotel_id)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="hotel bookings retrieved successfully",
            data=bookings
        )
    except ValueError as e:
        logger.warning("Failed to get hotel bookings: %s", e)
        if "not found" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="hotel with id not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        if "not authorized" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Opps! seems like you are not authorized to take this action for this hotel"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_response)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error getting hotel bookings: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


# ====================
# Dashboard & Analytics Endpoints
# ====================

@router.get("/{owner_id}/revenue-summary")
async def get_merchant_revenue_summary(owner_id: str) -> Dict[str, Any]:
    """Get revenue summary for all merchant's hotels"""
    try:
        summary = await MerchantService.get_merchant_revenue_summary(owner_id)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="revenue summary retrieved successfully",
            data=summary
        )
    except ValueError as e:
        logger.warning("Failed to get revenue summary: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error getting revenue summary: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("/{owner_id}/hotels/{hotel_id}/dashboard")
async def get_hotel_dashboard_stats(owner_id: str, hotel_id: str) -> Dict[str, Any]:
    """Get dashboard statistics for a specific hotel"""
    try:
        stats = await MerchantService.get_hotel_dashboard_stats(owner_id, hotel_id)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="hotel dashboard stats retrieved successfully",
            data=stats
        )
    except ValueError as e:
        logger.warning("Failed to get hotel dashboard stats: %s", e)
        if "not found" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="hotel with id not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        if "not authorized" in str(e).lower():
            error_response = create_response(
                status_code=status.HTTP_403_FORBIDDEN,
                message="Opps! seems like you are not authorized to take this action for this hotel"
            )
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_response)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Failed to get hotel dashboard stats, error: {}".format(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error getting hotel dashboard stats: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Opps an error occurred. Try again"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)
