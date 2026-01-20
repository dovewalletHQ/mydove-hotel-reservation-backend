from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.models.hotel import HotelSuite
from app.models.money import Money
from app.services.hotel_suites import HotelSuiteService
from app.core.logger import logger

router = APIRouter()


class HotelSuiteCreateRequest(BaseModel):
    hotel_id: str = Field(...)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
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


@router.post("/", response_model=HotelSuite, status_code=status.HTTP_201_CREATED)
async def create_hotel_suite(request: HotelSuiteCreateRequest):
    """Create a new hotel suite."""
    try:
        data = request.model_dump()
        # Convert price and currency to Money type
        data["price"] = Money(amount=data.pop("price"), currency=data.pop("currency"))
        suite = await HotelSuiteService.create_hotel_suite(HotelSuite(**data))
        return suite
    except ValueError as e:
        logger.warning("Failed to create hotel suite: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error creating hotel suite: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=List[HotelSuite])
async def get_all_suites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_available: Optional[bool] = None,
):
    """Get all hotel suites with optional filtering."""
    try:
        suites = await HotelSuiteService.get_all_suites()
        if is_available is not None:
            suites = [s for s in suites if s.is_available == is_available]
        return suites[skip : skip + limit]
    except Exception as e:
        logger.error("Unexpected error fetching suites: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{suite_id}", response_model=HotelSuite)
async def get_suite(suite_id: str):
    """Get a hotel suite by ID."""
    try:
        suite = await HotelSuiteService.get_suite_by_id(suite_id)
        if not suite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")
        return suite
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching suite: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/hotel/{hotel_id}", response_model=List[HotelSuite])
async def get_suites_by_hotel(hotel_id: str, is_available: Optional[bool] = None):
    """Get all suites for a specific hotel."""
    try:
        suites = await HotelSuiteService.get_suites_by_hotel(hotel_id)
        if is_available is not None:
            suites = [s for s in suites if s.is_available == is_available]
        return suites
    except Exception as e:
        logger.error("Unexpected error fetching suites by hotel: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{suite_id}", response_model=HotelSuite)
async def update_suite(suite_id: str, request: HotelSuiteUpdateRequest):
    """Update a hotel suite."""
    try:
        update_data = request.model_dump(exclude_unset=True)
        # Handle price/currency updates
        if "price" in update_data or "currency" in update_data:
            # Get existing suite to preserve currency if only price is updated
            existing_suite = await HotelSuiteService.get_suite_by_id(suite_id)
            if not existing_suite:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")

            price = update_data.pop("price", existing_suite.price.amount)
            currency = update_data.pop("currency", existing_suite.price.currency)
            update_data["price"] = Money(amount=price, currency=currency)

        suite = await HotelSuiteService.update_suite(suite_id, update_data)
        if not suite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")
        return suite
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Failed to update suite: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error updating suite: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/{suite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_suite(suite_id: str):
    """Delete a hotel suite."""
    try:
        result = await HotelSuiteService.delete_suite(suite_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error deleting suite: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{suite_id}/availability", response_model=HotelSuite)
async def toggle_suite_availability(suite_id: str, is_available: bool):
    """Toggle suite availability."""
    try:
        suite = await HotelSuiteService.update_suite(suite_id, {"is_available": is_available})
        if not suite:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suite not found")
        return suite
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error toggling suite availability: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

