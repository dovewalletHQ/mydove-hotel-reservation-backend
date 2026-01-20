import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.routers import api_router
from app.models.admin import Admin, AdminAuditLog, AdminAction
from app.models.hotel import Hotel
from app.services.admin import AdminService


@pytest.fixture
def app():
    """Create test FastAPI app."""
    app = FastAPI()
    app.include_router(api_router)
    return app


@pytest.fixture
async def client(app):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


class TestAdminRouter:
    @pytest.mark.anyio
    async def test_create_admin_success(self, client, mocker):
        # Arrange
        mock_admin = Admin(
            user_id="user123",
            role="admin",
            permissions=["approve_hotel"],
        )
        mocker.patch.object(AdminService, "create_admin", return_value=mock_admin)

        # Act
        response = await client.post(
            "/admin/",
            json={"user_id": "user123", "role": "admin", "permissions": ["approve_hotel"]},
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == "user123"
        assert data["role"] == "admin"

    @pytest.mark.anyio
    async def test_get_pending_hotels(self, client, mocker):
        # Arrange
        mock_hotels = [
            Hotel(name="Pending Hotel 1", owner_id="owner1", is_approved=False),
            Hotel(name="Pending Hotel 2", owner_id="owner2", is_approved=False),
        ]
        mocker.patch.object(AdminService, "get_pending_hotels", return_value=mock_hotels)

        # Act
        response = await client.get("/admin/hotels/pending")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.anyio
    async def test_approve_hotel_success(self, client, mocker):
        # Arrange
        mock_hotel = Hotel(name="Approved Hotel", owner_id="owner1", is_approved=True)
        mocker.patch.object(AdminService, "approve_hotel", return_value=mock_hotel)

        # Act
        response = await client.post(
            "/admin/hotels/hotel123/approve",
            headers={"X-Admin-Id": "admin123"},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["is_approved"] == True

    @pytest.mark.anyio
    async def test_approve_hotel_missing_admin_header(self, client):
        # Act - missing X-Admin-Id header
        response = await client.post("/admin/hotels/hotel123/approve")

        # Assert
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_reject_hotel_success(self, client, mocker):
        # Arrange
        mock_hotel = Hotel(name="Rejected Hotel", owner_id="owner1", is_approved=False)
        mocker.patch.object(AdminService, "reject_hotel", return_value=mock_hotel)

        # Act
        response = await client.post(
            "/admin/hotels/hotel123/reject",
            headers={"X-Admin-Id": "admin123"},
            json={"reason": "Does not meet standards"},
        )

        # Assert
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_suspend_user_success(self, client, mocker):
        # Arrange
        mocker.patch.object(AdminService, "suspend_user", return_value=True)

        # Act
        response = await client.post(
            "/admin/users/user123/suspend",
            headers={"X-Admin-Id": "admin123"},
            json={"reason": "Violation of terms"},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == "User suspended successfully"

    @pytest.mark.anyio
    async def test_get_audit_logs(self, client, mocker):
        # Arrange
        mock_logs = [
            AdminAuditLog(
                admin_id="admin123",
                action=AdminAction.APPROVE_HOTEL,
                target_id="hotel123",
                target_type="hotel",
                details={"reason": "Approved"},
            ),
        ]
        mocker.patch.object(AdminService, "get_audit_logs", return_value=mock_logs)

        # Act
        response = await client.get("/admin/audit-logs")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.anyio
    async def test_get_all_admins(self, client, mocker):
        # Arrange
        mock_admins = [
            Admin(user_id="user1", role="admin", permissions=[]),
            Admin(user_id="user2", role="super_admin", permissions=["all"]),
        ]
        mocker.patch.object(AdminService, "get_all_admins", return_value=mock_admins)

        # Act
        response = await client.get("/admin/")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2

