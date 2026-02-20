import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.hotel import HotelSuite, Hotel, HotelProfile
from app.models.booking import Booking

# Global client reference for connection management
_client: AsyncIOMotorClient = None


load_dotenv(verbose=True)
async def init_db():
    """
    Initialize the MongoDB connection and Beanie ODM.
    """
    # Use environment variables for configuration with defaults
    if os.getenv("ENVIRONMENT") == "production":
        mongo_dsn = os.getenv("DATABASE_URL")
        db_name = os.getenv("MONGO_DB_NAME")
    else:
        mongo_dsn = "mongodb://localhost:27017"
        db_name = "sandbox"

    print(f"=== Connecting to MongoDB at {mongo_dsn}, using database '{db_name}' ===")
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
    await init_db()


async def close_mongo_connection():
    """
    Close the MongoDB connection.
    Called during application shutdown.
    """
    global _client
    if _client:
        _client.close()

