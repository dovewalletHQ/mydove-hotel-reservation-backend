"""Review Service - Business logic layer for review operations"""

from datetime import datetime, timedelta
from typing import List, Optional

from app.core.logger import setup_logger
from app.models.booking import Booking, BookingStatus
from app.models.review import (
    Review,
    OwnerReply,
    CreateReviewRequest,
    UpdateReviewRequest,
    OwnerReplyRequest,
    ReviewResponse,
)
from app.repositories.review import ReviewRepository
from app.repositories.hotel import HotelRepository

logger = setup_logger(name="review_service")

# Maximum number of days after checkout a guest can leave a review
REVIEW_WINDOW_DAYS = 30


class ReviewService:
    """Service for handling review business logic"""

    # ─── Create ─────────────────────────────────────────────────────────

    @staticmethod
    async def create_review(request: CreateReviewRequest) -> ReviewResponse:
        """
        Create a new review for a hotel.

        Rules enforced:
        1. The booking must exist and belong to the reviewer (matched by phone).
        2. The booking must be in CHECKED_OUT or COMPLETED status.
        3. The review must be within 30 days of checkout.
        4. One review per booking.
        """
        # 1. Validate booking exists
        booking = await Booking.find_one(Booking.id == request.booking_id)
        if booking is None:
            # Try with ObjectId
            from bson import ObjectId
            if ObjectId.is_valid(request.booking_id):
                booking = await Booking.get(ObjectId(request.booking_id))
        if booking is None:
            raise ValueError("Booking not found")

        # 2. Verify the reviewer matches the booking guest
        if booking.guest_phone != request.reviewer_phone:
            raise ValueError("You can only review a booking that belongs to you")

        # 3. Booking must be checked out or completed
        if booking.status not in (BookingStatus.CHECKED_OUT, BookingStatus.COMPLETED):
            raise ValueError(
                "You can only review after checkout. "
                f"Current booking status: {booking.status.value}"
            )

        # 4. Check the 30-day review window
        checkout_date = booking.check_out_date
        if datetime.now() > checkout_date + timedelta(days=REVIEW_WINDOW_DAYS):
            raise ValueError(
                f"Review window has expired. You can only review within "
                f"{REVIEW_WINDOW_DAYS} days of checkout."
            )

        # 5. One review per booking
        existing = await ReviewRepository.get_review_by_booking_id(request.booking_id)
        if existing is not None:
            raise ValueError("You have already reviewed this booking")

        # 6. Validate hotel exists
        hotel = await HotelRepository.get_hotel_by_id(request.hotel_id)
        if hotel is None:
            raise ValueError("Hotel not found")

        # Create the review
        review = Review(
            hotel_id=request.hotel_id,
            booking_id=request.booking_id,
            reviewer_name=request.reviewer_name,
            reviewer_phone=request.reviewer_phone,
            reviewer_avatar_url=request.reviewer_avatar_url,
            rating=request.rating,
            comment=request.comment,
        )
        review = await ReviewRepository.create_review(review)

        # Update the hotel's aggregate rating
        await ReviewService._update_hotel_rating(request.hotel_id)

        logger.info("Review created for hotel '%s' by '%s'", request.hotel_id[:7], request.reviewer_name)
        return ReviewService._to_response(review)

    # ─── Read ───────────────────────────────────────────────────────────

    @staticmethod
    async def get_review_by_id(review_id: str) -> ReviewResponse:
        """Get a single review by its ID"""
        review = await ReviewRepository.get_review_by_id(review_id)
        if review is None:
            raise ValueError("Review not found")
        return ReviewService._to_response(review)

    @staticmethod
    async def get_reviews_by_hotel(
        hotel_id: str, skip: int = 0, limit: int = 20
    ) -> List[ReviewResponse]:
        """Get all reviews for a hotel (paginated, newest first)"""
        reviews = await ReviewRepository.get_reviews_by_hotel_id(hotel_id, skip, limit)
        return [ReviewService._to_response(r) for r in reviews]

    # ─── Update ─────────────────────────────────────────────────────────

    @staticmethod
    async def update_review(
        review_id: str, request: UpdateReviewRequest
    ) -> ReviewResponse:
        """
        Update a review. Only the original reviewer can update.
        Only rating and comment can be changed.
        """
        review = await ReviewRepository.get_review_by_id(review_id)
        if review is None:
            raise ValueError("Review not found")

        # Verify ownership
        if review.reviewer_phone != request.reviewer_phone:
            raise ValueError("You can only edit your own review")

        # Apply updates
        if request.rating is not None:
            review.rating = request.rating
        if request.comment is not None:
            review.comment = request.comment
        review.updatedAt = datetime.now()

        review = await ReviewRepository.update_review(review)

        # Recalculate hotel rating if rating changed
        if request.rating is not None:
            await ReviewService._update_hotel_rating(review.hotel_id)

        logger.info("Review '%s' updated", review_id[:7])
        return ReviewService._to_response(review)

    # ─── Delete ─────────────────────────────────────────────────────────

    @staticmethod
    async def delete_review(review_id: str, requester_phone: str) -> bool:
        """
        Delete a review. The original reviewer can delete their own review.
        """
        review = await ReviewRepository.get_review_by_id(review_id)
        if review is None:
            raise ValueError("Review not found")

        if review.reviewer_phone != requester_phone:
            raise ValueError("You can only delete your own review")

        hotel_id = review.hotel_id
        deleted = await ReviewRepository.delete_review(review_id)

        if deleted:
            # Recalculate hotel rating
            await ReviewService._update_hotel_rating(hotel_id)
            logger.info("Review '%s' deleted", review_id[:7])

        return deleted

    # ─── Owner Reply ────────────────────────────────────────────────────

    @staticmethod
    async def add_owner_reply(
        review_id: str, request: OwnerReplyRequest
    ) -> ReviewResponse:
        """
        Add an owner reply to a review.
        Validates that the owner actually owns the hotel being reviewed.
        """
        review = await ReviewRepository.get_review_by_id(review_id)
        if review is None:
            raise ValueError("Review not found")

        if review.owner_reply is not None:
            raise ValueError("This review already has an owner reply")

        # Verify the owner actually owns this hotel
        hotel = await HotelRepository.get_hotel_by_id(review.hotel_id)
        if hotel is None:
            raise ValueError("Hotel not found")
        if hotel.owner_id != request.owner_id:
            raise ValueError("Only the hotel owner can reply to reviews")

        review.owner_reply = OwnerReply(
            owner_id=request.owner_id,
            owner_name=request.owner_name,
            comment=request.comment,
        )
        review.updatedAt = datetime.now()
        review = await ReviewRepository.update_review(review)

        logger.info("Owner reply added to review '%s'", review_id[:7])
        return ReviewService._to_response(review)

    # ─── Helpers ────────────────────────────────────────────────────────

    @staticmethod
    async def _update_hotel_rating(hotel_id: str) -> None:
        """Recalculate and store the aggregate rating on the Hotel document"""
        avg_rating = await ReviewRepository.get_average_rating_by_hotel_id(hotel_id)
        total_reviews = await ReviewRepository.count_reviews_by_hotel_id(hotel_id)

        await HotelRepository.update_hotel(
            hotel_id,
            {"average_rating": avg_rating, "total_reviews": total_reviews},
        )

    @staticmethod
    def _to_response(review: Review) -> ReviewResponse:
        """Convert a Review document to a ReviewResponse"""
        return ReviewResponse(
            review_id=str(review.id),
            hotel_id=review.hotel_id,
            booking_id=review.booking_id,
            reviewer_name=review.reviewer_name,
            reviewer_phone=review.reviewer_phone,
            reviewer_avatar_url=review.reviewer_avatar_url,
            rating=review.rating,
            comment=review.comment,
            owner_reply=review.owner_reply,
            created_at=review.createdAt,
        )
