"""Hotel Profile Router - API endpoints for hotel profile management"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.hotel import HotelProfile
from app.services.hotel_profile import HotelProfileService
from app.core.logger import logger
from app.utils.response import create_response

router = APIRouter()


class HotelProfileCreateRequest(BaseModel):
    hotel_id: str = Field(...)
    description: Optional[str] = None
    website_url: Optional[str] = None
    display_photo_url: Optional[List[str]] = None
    instagram_handle: Optional[str] = None
    facebook_handle: Optional[str] = None
    twitter_handle: Optional[str] = None


class HotelProfileUpdateRequest(BaseModel):
    description: Optional[str] = None
    website_url: Optional[str] = None
    display_photo_url: Optional[List[str]] = None
    instagram_handle: Optional[str] = None
    facebook_handle: Optional[str] = None
    twitter_handle: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_hotel_profile(request: HotelProfileCreateRequest):
    """Create a new hotel profile."""
    try:
        profile = await HotelProfileService.create_hotel_profile(
            HotelProfile(**request.model_dump())
        )
        if isinstance(profile, str):
            raise ValueError(profile)
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Hotel profile created successfully",
            data=profile.model_dump(),
        )
    except ValueError as e:
        logger.warning("Failed to create hotel profile: %s", e)
        error_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
    except Exception as e:
        logger.error("Unexpected error creating hotel profile: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)


@router.get("/{hotel_id}", response_model=HotelProfile)
async def get_profile_by_hotel(hotel_id: str):
    """Get the profile for a specific hotel."""
    try:
        profile = await HotelProfileService.get_hotel_profile_by_hotel_id(hotel_id)
        if isinstance(profile, str):
            err_response = create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=profile,
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_response)
        if not profile:
            err_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Profile not found for this hotel",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_response)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching profile by hotel: %s", e)
        err_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err_response)


@router.patch("/{hotel_id}")
async def update_profile(hotel_id: str, request: HotelProfileUpdateRequest):
    """Update a hotel profile."""
    try:
        # Get existing profile first
        existing = await HotelProfileService.get_hotel_profile_by_hotel_id(hotel_id)
        if isinstance(existing, str):
            err_response = create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=existing,
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_response)
        if not existing:
            err_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Profile not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err_response)

        # Update fields
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(existing, key, value)

        profile = await HotelProfileService.update_hotel_profile(existing)
        if isinstance(profile, str):
            raise ValueError(profile)

        return create_response(
            status_code=status.HTTP_200_OK,
            message="Hotel profile updated successfully",
            data=profile.model_dump(),
        )
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Failed to update profile: %s", e)
        err_response = create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_response)
    except Exception as e:
        logger.error("Unexpected error updating profile: %s", e)
        err_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err_response)


@router.delete("/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(hotel_id: str):
    """Delete a hotel profile."""
    try:
        result = await HotelProfileService.delete_hotel_profile(hotel_id)
        if isinstance(result, str):
            error_response = create_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                message=result,
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_response)
        if not result:
            error_response = create_response(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Profile not found",
            )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_response)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Hotel profile deleted successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error deleting profile: %s", e)
        error_response = create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An unexpected error occurred"
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_response)
