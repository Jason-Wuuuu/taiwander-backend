from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ..core.settings import settings
from ..core.exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect_to_database(cls):
        """Create database connection."""
        try:
            logger.info("Connecting to MongoDB...")
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            logger.info("Connected to MongoDB")

            # Create collections and indexes if they don't exist
            await cls._setup_collections()

            return cls.client
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise DatabaseError(f"Failed to connect to database: {str(e)}")

    @classmethod
    async def close_database_connection(cls):
        """Close database connection."""
        if cls.client:
            logger.info("Closing MongoDB connection...")
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    async def _setup_collections(cls):
        """Initialize collections and create indexes."""
        # Create attractions collection if it doesn't exist
        if "attractions" not in await cls.db.list_collection_names():
            # Create attractions collection
            await cls.db.create_collection("attractions")

        # Create indexes for better query performance
        # No need to index _id as MongoDB does this automatically

        # Text search index for the search() method
        await cls.db.attractions.create_index([("attractionName", "text"), ("description", "text")])

        # Index for filtering by class in find_by_classes() and find_with_filters()
        await cls.db.attractions.create_index([("attractionClasses", 1)])

        # Geospatial index for find_nearby() and count_nearby()
        await cls.db.attractions.create_index([("location", "2dsphere")])

        # Index for filtering by region in find_by_region() and find_with_filters()
        await cls.db.attractions.create_index([("postalAddress.city", 1)])

        # Index for filtering free attractions in find_free_attractions() and find_with_filters()
        await cls.db.attractions.create_index([("isAccessibleForFree", 1)])

        logger.info("MongoDB collections and indexes set up successfully")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if not cls.db:
            raise DatabaseError("Database connection not established")
        return cls.db

# Dependency to get database


async def get_database() -> AsyncIOMotorDatabase:
    return MongoDB.get_database()
