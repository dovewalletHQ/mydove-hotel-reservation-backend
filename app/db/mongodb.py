import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.hotel import HotelSuite, Hotel, HotelProfile
from app.models.booking import Booking

# Global client reference for connection management
_client: AsyncIOMotorClient = None


async def init_db():
    """
    Initialize the MongoDB connection and Beanie ODM.
    """
    # Use environment variables for configuration with defaults
    mongo_dsn = os.getenv("MONGO_DSN", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "sandbox")

    client = AsyncIOMotorClient(mongo_dsn)
    
    # Initialize Beanie with the database and document models
    await init_beanie(
        database=client[db_name],
        document_models=[
            HotelSuite,
            Hotel,
            HotelProfile,
            Booking,
        ]
    )


async def connect_to_mongo():
    """
    Connect to MongoDB and initialize Beanie ODM.
    Called during application startup.
    """
    global _client
    mongo_dsn = os.getenv("MONGO_DSN", "mongodb://localhost:27017")
    db_name = os.getenv("MONGO_DB_NAME", "sandbox")

    _client = AsyncIOMotorClient(mongo_dsn)

    await init_beanie(
        database=_client[db_name],
        document_models=[
            HotelSuite,
            Hotel,
            HotelProfile,
            Booking,
        ]
    )


async def close_mongo_connection():
    """
    Close the MongoDB connection.
    Called during application shutdown.
    """
    global _client
    if _client:
        _client.close()

