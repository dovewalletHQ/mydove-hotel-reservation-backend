"""Review repository - Database operations for reviews"""

from typing import Optional, List

from bson import ObjectId

from app.models.review import Review
from app.core.logger import logger


class ReviewRepository:
    """Handles database operations for hotel reviews"""

    @staticmethod
    async def create_review(review: Review) -> Review:
        """Save a new review to the database"""
        await review.save()
        return review

    @staticmethod
    async def get_review_by_id(review_id: str) -> Optional[Review]:
        """Get a review by its ID"""
        if not ObjectId.is_valid(review_id):
            return None
        return await Review.get(ObjectId(review_id))

    @staticmethod
    async def get_review_by_booking_id(booking_id: str) -> Optional[Review]:
        """Get a review tied to a specific booking (enforces one review per booking)"""
        return await Review.find_one(Review.booking_id == booking_id)

    @staticmethod
    async def get_reviews_by_hotel_id(
        hotel_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Review]:
        """Get all reviews for a hotel, ordered by newest first"""
        return (
            await Review.find(Review.hotel_id == hotel_id)
            .sort(-Review.createdAt)
            .skip(skip)
            .limit(limit)
            .to_list()
        )

    @staticmethod
    async def count_reviews_by_hotel_id(hotel_id: str) -> int:
        """Count total reviews for a hotel"""
        return await Review.find(Review.hotel_id == hotel_id).count()

    @staticmethod
    async def get_average_rating_by_hotel_id(hotel_id: str) -> float:
        """Calculate the average rating for a hotel"""
        reviews = await Review.find(Review.hotel_id == hotel_id).to_list()
        if not reviews:
            return 0.0
        total = sum(r.rating for r in reviews)
        return round(total / len(reviews), 1)

    @staticmethod
    async def update_review(review: Review) -> Review:
        """Update an existing review"""
        await review.save()
        return review

    @staticmethod
    async def delete_review(review_id: str) -> bool:
        """Delete a review by its ID"""
        review = await ReviewRepository.get_review_by_id(review_id)
        if review is None:
            return False
        await review.delete()
        return True
