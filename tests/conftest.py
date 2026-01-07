import pytest
from app.db.mongodb import init_db

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Initialize the database connection for the test session."""
    await init_db()
