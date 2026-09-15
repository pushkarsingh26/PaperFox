import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger("paperfox.database")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

db_instance = Database()


async def connect_to_mongo():
    if not settings.MONGODB_URL:
        raise ValueError("MONGODB_URL is not configured in settings.")
    
    logger.info(f"Connecting to MongoDB...")
    db_instance.client = AsyncIOMotorClient(settings.MONGODB_URL)
    db_instance.db = db_instance.client[settings.DATABASE_NAME]
    
    try:
        # Create indexes
        users_collection = db_instance.db["users"]
        await users_collection.create_index("email", unique=True)
        
        sessions_collection = db_instance.db["sessions"]
        await sessions_collection.create_index("token_hash", unique=True)
        await sessions_collection.create_index("user_id")
        await sessions_collection.create_index("expires_at", expireAfterSeconds=0)
        
        profiles_collection = db_instance.db["candidate_profiles"]
        await profiles_collection.create_index("user_id", unique=True)
        
        logger.info("MongoDB connection established successfully and indexes ensured.")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB database connection/indexes: {e}")
        raise e


async def close_mongo_connection():
    if db_instance.client:
        logger.info("Closing MongoDB connection...")
        db_instance.client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> AsyncIOMotorDatabase:
    if db_instance.db is None:
        raise RuntimeError("Database connection is not initialized.")
    return db_instance.db
