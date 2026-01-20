"""Admin Models - Data structures for admin operations"""

from enum import Enum
from typing import List, Optional

from pydantic import Field

from app.models.base import BaseMongoModel


class AdminAction(str, Enum):
    """Enum for admin action types for audit logging"""
    APPROVE_HOTEL = "approve_hotel"
    REJECT_HOTEL = "reject_hotel"
    SUSPEND_USER = "suspend_user"
    UNSUSPEND_USER = "unsuspend_user"
    SUSPEND_MERCHANT = "suspend_merchant"
    UNSUSPEND_MERCHANT = "unsuspend_merchant"
    DELETE_USER = "delete_user"
    DELETE_MERCHANT = "delete_merchant"
    DELETE_HOTEL = "delete_hotel"
    UPDATE_HOTEL = "update_hotel"
    CREATE_ADMIN = "create_admin"
    UPDATE_ADMIN = "update_admin"
    DELETE_ADMIN = "delete_admin"
    VIEW_AUDIT_LOG = "view_audit_log"


class AdminAuditLog(BaseMongoModel):
    """Audit log for tracking admin actions"""
    admin_id: str = Field(..., description="ID of the admin who performed the action")
    action: AdminAction = Field(..., description="The action performed")
    target_id: str = Field(..., description="ID of the target entity")
    target_type: str = Field(..., description="Type of target: hotel, user, merchant, admin")
    details: dict = Field(default_factory=dict, description="Additional details about the action")
    reason: Optional[str] = Field(default=None, description="Reason for the action")

    class Settings:
        name = "admin_audit_logs"


class Admin(BaseMongoModel):
    """Admin user model"""
    user_id: str = Field(..., description="Reference to base user ID")
    role: str = Field(default="admin", description="Admin role: super_admin, admin, moderator")
    permissions: List[str] = Field(default_factory=list, description="List of permission strings")
    is_active: bool = Field(default=True, description="Whether the admin account is active")

    class Settings:
        name = "admins"

