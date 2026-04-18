"""Review router - CRUD endpoints for hotel reviews"""

from fastapi import APIRouter, HTTPException, Query, status

from app.core.logger import setup_logger
from app.utils.response import create_response
from app.models.review import (
    CreateReviewRequest,
    UpdateReviewRequest,
    OwnerReplyRequest,
)
from app.services.review import ReviewService

logger = setup_logger(name="review_router")

router = APIRouter()


# ─── Create ─────────────────────────────────────────────────────────────────


@router.post("")
async def create_review(req: CreateReviewRequest):
    """
    Create a new hotel review.

    Rules:
    - The booking must be CHECKED_OUT or COMPLETED.
    - Must be within 30 days of checkout.
    - One review per booking.
    """
    try:
        review = await ReviewService.create_review(req)
        return create_response(
            status_code=status.HTTP_201_CREATED,
            message="Review created successfully",
            data=review,
        )
    except ValueError as e:
        logger.error("Error creating review: %s", e)
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
    except Exception as e:
        logger.error("Unexpected error creating review: %s", e)
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while creating the review",
        )

# ─── Read ───────────────────────────────────────────────────────────────────


@router.get("/hotel/{hotel_id}")
async def get_reviews_by_hotel(
    hotel_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """Get all reviews for a hotel (paginated, newest first)."""
    try:
        reviews = await ReviewService.get_reviews_by_hotel(hotel_id, skip, limit)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Reviews retrieved successfully",
            data=reviews,
        )
    except Exception as e:
        logger.error("Error fetching reviews for hotel '%s': %s", hotel_id[:7], e)
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while fetching reviews",
        )

@router.get("/{review_id}")
async def get_review(review_id: str):
    """Get a single review by its ID."""
    try:
        review = await ReviewService.get_review_by_id(review_id)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Review retrieved successfully",
            data=review,
        )
    except ValueError as e:
        logger.error("Review not found: %s", e)
        return create_response(
            status_code=status.HTTP_404_NOT_FOUND,
            message=str(e),
        )
    except Exception as e:
        logger.error("Error fetching review '%s': %s", review_id[:7], e)
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while fetching the review",
        )


# ─── Update ─────────────────────────────────────────────────────────────────


@router.patch("/{review_id}")
async def update_review(
    review_id: str,
    req: UpdateReviewRequest,
    reviewer_phone: str = Query(..., description="Phone number of the reviewer (for ownership verification)"),
):
    """Update a review. Only the original reviewer can update their review."""
    try:
        review = await ReviewService.update_review(review_id, reviewer_phone, req)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Review updated successfully",
            data=review,
        )
    except ValueError as e:
        logger.error("Error updating review '%s': %s", review_id[:7], e)
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
    except Exception as e:
        logger.error("Unexpected error updating review '%s': %s", review_id[:7], e)
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while updating the review",
        )


# ─── Delete ─────────────────────────────────────────────────────────────────


@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    reviewer_phone: str = Query(..., description="Phone number of the reviewer (for ownership verification)"),
):
    """Delete a review. Only the original reviewer can delete their review."""
    try:
        await ReviewService.delete_review(review_id, reviewer_phone)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Review deleted successfully",
        )
    except ValueError as e:
        logger.error("Error deleting review '%s': %s", review_id[:7], e)
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
    except Exception as e:
        logger.error("Unexpected error deleting review '%s': %s", review_id[:7], e)
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while deleting the review",
        )


# ─── Owner Reply ────────────────────────────────────────────────────────────


@router.post("/{review_id}/reply")
async def add_owner_reply(review_id: str, req: OwnerReplyRequest):
    """
    Add a hotel owner's reply to a review.
    Only the owner of the reviewed hotel can reply.
    """
    try:
        review = await ReviewService.add_owner_reply(review_id, req)
        return create_response(
            status_code=status.HTTP_200_OK,
            message="Reply added successfully",
            data=review,
        )
    except ValueError as e:
        logger.error("Error adding reply to review '%s': %s", review_id[:7], e)
        return create_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=str(e),
        )
    except Exception as e:
        logger.error("Unexpected error adding reply to review '%s': %s", review_id[:7], e)
        return create_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="An error occurred while adding the reply",
        )
