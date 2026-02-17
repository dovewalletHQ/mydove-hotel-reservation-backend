from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.models.hotel import Hotel, HotelResponse
from app.services.hotel import HotelService
from app.core.logger import logger
from app.utils.response import create_response

router = APIRouter()


class HotelCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    owner_id: str = Field(...)
    address: Optional[str] = None
    city: str = Field(...)
    state: str = Field(...)
    country: str = Field(...)
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude of the hotel")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude of the hotel")

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if hasattr(self, 'latitude') and hasattr(self, 'longitude') and self.latitude is not None and self.longitude is not None:
             data['location'] = {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude]
            }
             # Remove lat/long from data as they are now in location
             data.pop('latitude', None)
             data.pop('longitude', None)
        return data


class HotelUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    is_available: Optional[bool] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude of the hotel")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude of the hotel")

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        if hasattr(self, 'latitude') and hasattr(self, 'longitude') and self.latitude is not None and self.longitude is not None:
             data['location'] = {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude]
            }
             # Remove lat/long from data as they are now in location
             data.pop('latitude', None)
             data.pop('longitude', None)
        return data


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_hotel(request: HotelCreateRequest):
    """Create a new hotel."""
    try:
        hotel = await HotelService.create_hotel(Hotel(**request.model_dump()))
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Hotel created successfully",
            data=hotel,
        )
    except ValueError as e:
        logger.warning("Failed to create hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error creating hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("")
async def get_all_hotels(
    skip: int = Query(0, ge=0),
    limit: int = Query(40, ge=1, le=100),
    is_approved: Optional[bool] = None,
    is_available: Optional[bool] = None,
    lga: Optional[str] = None,
    state: Optional[str] = None,
    city: Optional[str] = None,
    # Geospatial search params
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Latitude for proximity search"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Longitude for proximity search"),
    radius_km: Optional[float] = Query(10.0, gt=0, description="Search radius in kilometers"),
):
    """Get all hotels with optional filtering.
    
    For geospatial search, provide both latitude and longitude.
    """
    try:
        hotels = await HotelService.get_all_hotels(
            skip=skip,
            limit=limit,
            is_approved=is_approved,
            is_open=is_available,
            state=state,
            lga=lga,
            city=city,
            latitude=latitude,
            longitude=longitude,
            radius_km=radius_km
        )
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Hotels retrieved successfully",
            data=hotels,
        )
    except Exception as e:
        logger.error("Unexpected error fetching hotels: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: str):
    """Get a hotel by ID."""
    try:
        hotel = await HotelService.get_hotel_by_id(hotel_id)
        if not hotel:
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Hotel not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        response_data = HotelResponse(**hotel.model_dump())
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Hotel retrieved successfully",
            data=response_data,
        )
    except ValueError as e:
        logger.warning("Failed to get hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("/owner/{owner_id}", response_model=List[Hotel])
async def get_hotels_by_owner(owner_id: str):
    """Get all hotels owned by a specific owner."""
    try:
        hotels = await HotelService.get_hotels_by_owner(owner_id)
        return hotels
    except ValueError as e:
        logger.warning("Failed to get hotels by owner: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error fetching hotels by owner: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.patch("/{hotel_id}", response_model=Hotel)
async def update_hotel(hotel_id: str, request: HotelUpdateRequest):
    """Update a hotel."""
    try:
        update_data = request.model_dump(exclude_unset=True)
        hotel = await HotelService.update_hotel(hotel_id, update_data)
        if not hotel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
        return hotel
    except ValueError as e:
        logger.warning("Failed to update hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error updating hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.delete("/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hotel(hotel_id: str):
    """Delete a hotel."""
    try:
        result = await HotelService.delete_hotel(hotel_id)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel not found")
        return create_response(
            status_code=status.HTTP_204_NO_CONTENT,
            message="Hotel deleted successfully",
        )
    except ValueError as e:
        logger.warning("Failed to delete hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error deleting hotel: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)
