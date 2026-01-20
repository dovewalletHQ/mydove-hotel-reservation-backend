import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

from app.routers import api_router
from app.models.hotel import Hotel
from app.services.hotel import HotelService


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


class TestHotelRouter:
    @pytest.mark.anyio
    async def test_create_hotel_success(self, client, mocker):
        # Arrange
        mock_hotel = Hotel(
            name="Test Hotel",
            owner_id="owner123",
            is_approved=False,
        )
        mocker.patch.object(HotelService, "create_hotel", return_value=mock_hotel)

        # Act
        response = await client.post(
            "/hotels/",
            json={"name": "Test Hotel", "owner_id": "owner123"},
        )

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Hotel"
        assert data["owner_id"] == "owner123"

    @pytest.mark.anyio
    async def test_create_hotel_validation_error(self, client):
        # Act - missing required field
        response = await client.post(
            "/hotels/",
            json={"name": "Test Hotel"},  # missing owner_id
        )

        # Assert
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_get_hotel_success(self, client, mocker):
        # Arrange
        mock_hotel = Hotel(
            name="Test Hotel",
            owner_id="owner123",
        )
        mocker.patch.object(HotelService, "get_hotel_by_id", return_value=mock_hotel)

        # Act
        response = await client.get("/hotels/someid123")

        # Assert
        assert response.status_code == 200
        assert response.json()["name"] == "Test Hotel"

    @pytest.mark.anyio
    async def test_get_hotel_not_found(self, client, mocker):
        # Arrange
        mocker.patch.object(HotelService, "get_hotel_by_id", return_value=None)

        # Act
        response = await client.get("/hotels/nonexistent")

        # Assert
        assert response.status_code == 404

    @pytest.mark.anyio
    async def test_get_all_hotels(self, client, mocker):
        # Arrange
        mock_hotels = [
            Hotel(name="Hotel 1", owner_id="owner1"),
            Hotel(name="Hotel 2", owner_id="owner2"),
        ]
        mocker.patch.object(HotelService, "get_all_hotels", return_value=mock_hotels)

        # Act
        response = await client.get("/hotels/")

        # Assert
        assert response.status_code == 200
        assert len(response.json()) == 2

    @pytest.mark.anyio
    async def test_update_hotel_success(self, client, mocker):
        # Arrange
        mock_hotel = Hotel(name="Updated Hotel", owner_id="owner123")
        mocker.patch.object(HotelService, "update_hotel", return_value=mock_hotel)

        # Act
        response = await client.patch(
            "/hotels/someid123",
            json={"name": "Updated Hotel"},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Hotel"

    @pytest.mark.anyio
    async def test_delete_hotel_success(self, client, mocker):
        # Arrange
        mocker.patch.object(HotelService, "delete_hotel", return_value=True)

        # Act
        response = await client.delete("/hotels/someid123")

        # Assert
        assert response.status_code == 204

    @pytest.mark.anyio
    async def test_delete_hotel_not_found(self, client, mocker):
        # Arrange
        mocker.patch.object(HotelService, "delete_hotel", return_value=False)

        # Act
        response = await client.delete("/hotels/nonexistent")

        # Assert
        assert response.status_code == 404

