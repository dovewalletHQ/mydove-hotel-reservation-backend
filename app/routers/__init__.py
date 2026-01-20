from fastapi import APIRouter

from app.routers.hotel import router as hotel_router
from app.routers.hotel_suite import router as hotel_suite_router
from app.routers.hotel_profile import router as hotel_profile_router
from app.routers.merchant import router as merchant_router

api_router = APIRouter()

api_router.include_router(hotel_router, prefix="/hotels", tags=["Hotels"])
api_router.include_router(hotel_suite_router, prefix="/suites", tags=["Hotel Suites"])
api_router.include_router(hotel_profile_router, prefix="/hotels/profile", tags=["Hotel Profiles"])
api_router.include_router(merchant_router, prefix="/merchants", tags=["Merchants"])

