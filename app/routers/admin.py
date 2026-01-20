from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Query, Header
from pydantic import BaseModel, Field

from app.models.admin import Admin, AdminAuditLog, AdminAction
from app.models.hotel import Hotel
from app.services.admin import AdminService
from app.core.logger import logger

router = APIRouter()


class AdminCreateRequest(BaseModel):
    user_id: str = Field(...)
    role: str = Field(default="admin")
    permissions: List[str] = Field(default_factory=list)


class AdminUpdateRequest(BaseModel):
    role: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class HotelApprovalRequest(BaseModel):
    reason: Optional[str] = None


class UserSuspendRequest(BaseModel):
    reason: str = Field(..., min_length=1)


# Admin CRUD endpoints
@router.post("/", response_model=Admin, status_code=status.HTTP_201_CREATED)
async def create_admin(request: AdminCreateRequest):
    """Create a new admin user."""
    try:
        admin = await AdminService.create_admin(Admin(**request.model_dump()))
        return admin
    except ValueError as e:
        logger.warning("Failed to create admin: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error creating admin: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/", response_model=List[Admin])
async def get_all_admins(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
):
    """Get all admins."""
    try:
        admins = await AdminService.get_all_admins()
        if is_active is not None:
            admins = [a for a in admins if a.is_active == is_active]
        return admins[skip : skip + limit]
    except Exception as e:
        logger.error("Unexpected error fetching admins: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/{admin_id}", response_model=Admin)
async def get_admin(admin_id: str):
    """Get an admin by ID."""
    try:
        admin = await AdminService.get_admin_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
        return admin
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching admin: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.patch("/{admin_id}", response_model=Admin)
async def update_admin(admin_id: str, request: AdminUpdateRequest):
    """Update an admin."""
    try:
        update_data = request.model_dump(exclude_unset=True)
        admin = await AdminService.update_admin(admin_id, update_data)
        if not admin:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
        return admin
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning("Failed to update admin: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error updating admin: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Hotel approval endpoints
@router.get("/hotels/pending", response_model=List[Hotel])
async def get_pending_hotels():
    """Get all hotels pending approval."""
    try:
        hotels = await AdminService.get_pending_hotels()
        return hotels
    except Exception as e:
        logger.error("Unexpected error fetching pending hotels: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/hotels/{hotel_id}/approve", response_model=Hotel)
async def approve_hotel(
    hotel_id: str,
    request: HotelApprovalRequest = None,
    x_admin_id: str = Header(..., alias="X-Admin-Id"),
):
    """Approve a hotel registration."""
    try:
        hotel = await AdminService.approve_hotel(hotel_id, x_admin_id)
        return hotel
    except ValueError as e:
        logger.warning("Failed to approve hotel: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error approving hotel: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/hotels/{hotel_id}/reject", response_model=Hotel)
async def reject_hotel(
    hotel_id: str,
    request: HotelApprovalRequest,
    x_admin_id: str = Header(..., alias="X-Admin-Id"),
):
    """Reject a hotel registration."""
    try:
        hotel = await AdminService.reject_hotel(hotel_id, x_admin_id, request.reason)
        return hotel
    except ValueError as e:
        logger.warning("Failed to reject hotel: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error rejecting hotel: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# User management endpoints
@router.post("/users/{user_id}/suspend", status_code=status.HTTP_200_OK)
async def suspend_user(
    user_id: str,
    request: UserSuspendRequest,
    x_admin_id: str = Header(..., alias="X-Admin-Id"),
):
    """Suspend a user account."""
    try:
        result = await AdminService.suspend_user(user_id, x_admin_id, request.reason)
        return {"message": "User suspended successfully", "user_id": user_id}
    except ValueError as e:
        logger.warning("Failed to suspend user: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error suspending user: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/users/{user_id}/unsuspend", status_code=status.HTTP_200_OK)
async def unsuspend_user(
    user_id: str,
    x_admin_id: str = Header(..., alias="X-Admin-Id"),
):
    """Unsuspend a user account."""
    try:
        result = await AdminService.unsuspend_user(user_id, x_admin_id)
        return {"message": "User unsuspended successfully", "user_id": user_id}
    except ValueError as e:
        logger.warning("Failed to unsuspend user: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error unsuspending user: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Merchant management endpoints
@router.post("/merchants/{merchant_id}/suspend", status_code=status.HTTP_200_OK)
async def suspend_merchant(
    merchant_id: str,
    request: UserSuspendRequest,
    x_admin_id: str = Header(..., alias="X-Admin-Id"),
):
    """Suspend a merchant account."""
    try:
        result = await AdminService.suspend_merchant(merchant_id, x_admin_id, request.reason)
        return {"message": "Merchant suspended successfully", "merchant_id": merchant_id}
    except ValueError as e:
        logger.warning("Failed to suspend merchant: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error suspending merchant: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# Audit log endpoints
@router.get("/audit-logs", response_model=List[AdminAuditLog])
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    admin_id: Optional[str] = None,
    action: Optional[AdminAction] = None,
    target_type: Optional[str] = None,
):
    """Get admin audit logs with optional filtering."""
    try:
        logs = await AdminService.get_audit_logs(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            skip=skip,
            limit=limit,
        )
        return logs
    except Exception as e:
        logger.error("Unexpected error fetching audit logs: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/audit-logs/{log_id}", response_model=AdminAuditLog)
async def get_audit_log(log_id: str):
    """Get a specific audit log entry."""
    try:
        log = await AdminService.get_audit_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit log not found")
        return log
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error fetching audit log: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

