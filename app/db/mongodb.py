import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.hotel import HotelSuite, Hotel, HotelProfile


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
            HotelProfile
        ]
    )
