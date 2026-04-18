"""Review model for hotel reviews"""

from datetime import datetime
from typing import Optional, List

from pydantic import Field, BaseModel, field_validator

from app.models.base import BaseMongoModel


class OwnerReply(BaseModel):
    """Embedded model for a hotel owner's reply to a review"""
    owner_id: str = Field(..., description="ID of the hotel owner who replied")
    owner_name: str = Field(..., min_length=1, description="Name of the hotel owner")
    comment: str = Field(..., min_length=1, max_length=2000, description="Owner's reply text")
    replied_at: datetime = Field(default_factory=datetime.now, description="When the reply was posted")


class Review(BaseMongoModel):
    """Data model for hotel reviews stored in MongoDB"""
    hotel_id: str = Field(..., description="ID of the hotel being reviewed")
    booking_id: str = Field(..., description="ID of the booking this review is tied to (one review per booking)")

    # Reviewer info (passed from the other service)
    reviewer_name: str = Field(..., min_length=1, description="Name of the reviewer")
    reviewer_phone: str = Field(..., min_length=1, description="Phone number of the reviewer")
    reviewer_avatar_url: Optional[str] = Field(default=None, description="Profile image URL of the reviewer")

    # Review content
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    comment: str = Field(..., min_length=1, max_length=5000, description="Review text")

    # Owner reply (optional, added later by the hotel owner)
    owner_reply: Optional[OwnerReply] = Field(default=None, description="Hotel owner's reply to this review")

    class Settings:
        name = "reviews"


# ─── Request / Response schemas ───────────────────────────────────────────────


class CreateReviewRequest(BaseModel):
    """Request model for creating a review"""
    hotel_id: str = Field(..., description="ID of the hotel being reviewed")
    booking_id: str = Field(..., description="Booking ID to tie this review to")
    reviewer_name: str = Field(..., min_length=1, description="Name of the reviewer")
    reviewer_phone: str = Field(..., min_length=1, description="Phone number of the reviewer")
    reviewer_avatar_url: Optional[str] = Field(default=None, description="Profile image URL")
    rating: int = Field(..., ge=1, le=5, description="Star rating (1-5)")
    comment: str = Field(..., min_length=1, max_length=5000, description="Review text")


class UpdateReviewRequest(BaseModel):
    """Request model for updating a review (only rating and comment can change)"""
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Updated star rating")
    comment: Optional[str] = Field(default=None, min_length=1, max_length=5000, description="Updated review text")


class OwnerReplyRequest(BaseModel):
    """Request model for a hotel owner to reply to a review"""
    owner_id: str = Field(..., description="ID of the hotel owner replying")
    owner_name: str = Field(..., min_length=1, description="Name of the hotel owner")
    comment: str = Field(..., min_length=1, max_length=2000, description="Reply text")


class ReviewResponse(BaseModel):
    """Response model for a single review"""
    review_id: str = Field(..., description="Unique identifier for this review")
    hotel_id: str = Field(..., description="Hotel ID")
    booking_id: str = Field(..., description="Booking ID")
    reviewer_name: str = Field(..., description="Reviewer name")
    reviewer_phone: str = Field(..., description="Reviewer phone")
    reviewer_avatar_url: Optional[str] = Field(default=None, description="Reviewer avatar URL")
    rating: int = Field(..., ge=1, le=5, description="Star rating")
    comment: str = Field(..., description="Review text")
    owner_reply: Optional[OwnerReply] = Field(default=None, description="Owner reply if any")
    created_at: datetime = Field(..., description="When the review was posted")
