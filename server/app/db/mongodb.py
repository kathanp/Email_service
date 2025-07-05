from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None

    @classmethod
    async def connect_to_mongo(cls):
        """Create database connection."""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.database = cls.client[settings.DATABASE_NAME]
            
            # Test the connection
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB Atlas")
            
            # Create indexes for better performance
            await cls.create_indexes()
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise

    @classmethod
    async def close_mongo_connection(cls):
        """Close database connection."""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    async def create_indexes(cls):
        """Create database indexes for better performance."""
        try:
            # Users collection indexes
            await cls.database.users.create_index("email", unique=True)
            await cls.database.users.create_index("created_at")
            
            # Customers collection indexes
            await cls.database.customers.create_index("email")
            await cls.database.customers.create_index("user_id")
            await cls.database.customers.create_index("status")
            
            # Email campaigns indexes
            await cls.database.email_campaigns.create_index("user_id")
            await cls.database.email_campaigns.create_index("status")
            await cls.database.email_campaigns.create_index("scheduled_at")
            
            # Email logs indexes
            await cls.database.email_logs.create_index("user_id")
            await cls.database.email_logs.create_index("campaign_id")
            await cls.database.email_logs.create_index("customer_id")
            await cls.database.email_logs.create_index("status")
            await cls.database.email_logs.create_index("sent_at")
            
            # Files collection indexes
            await cls.database.files.create_index("user_id")
            await cls.database.files.create_index("file_type")
            await cls.database.files.create_index("upload_date")
            await cls.database.files.create_index("is_active")
            
            # Templates collection indexes
            await cls.database.templates.create_index("user_id")
            await cls.database.templates.create_index("name")
            await cls.database.templates.create_index("created_at")
            await cls.database.templates.create_index("is_active")
            
            # Senders collection indexes
            await cls.database.senders.create_index("user_id")
            await cls.database.senders.create_index("email")
            await cls.database.senders.create_index("verification_status")
            await cls.database.senders.create_index("is_default")
            await cls.database.senders.create_index("created_at")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    @classmethod
    def get_database(cls):
        """Get database instance."""
        return cls.database

    @classmethod
    def get_collection(cls, collection_name: str):
        """Get collection instance."""
        return cls.database[collection_name]
