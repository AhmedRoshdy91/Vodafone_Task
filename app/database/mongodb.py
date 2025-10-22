"""
MongoDB Connection Manager with Context Manager Pattern
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.config import settings
from app.constants import (
    MongoDBCollections, 
    MongoDBIndexNames, 
    DatabasePoolSize,
    DatabaseTimeout
)
import logging

logger = logging.getLogger(__name__)


class MongoManager:
    """
    Singleton MongoDB connection manager with context manager support
    """
    
    _instance: Optional['MongoManager'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _db: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Initialize MongoDB client and setup schema"""
        if self._client is None:
            try:
                self._client = AsyncIOMotorClient(
                    settings.mongo_dsn,
                    maxPoolSize=DatabasePoolSize.MONGODB_MAX_POOL_SIZE,
                    minPoolSize=DatabasePoolSize.MONGODB_MIN_POOL_SIZE,
                    maxIdleTimeMS=DatabaseTimeout.MONGODB_MAX_IDLE_TIME * 1000,  # Convert to milliseconds
                    serverSelectionTimeoutMS=DatabaseTimeout.MONGODB_SERVER_SELECTION * 1000
                )
                self._db = self._client[settings.mongo_db]
                
                # Test connection
                await self._client.admin.command('ping')
                logger.info(f"MongoDB connection established (pool size: {DatabasePoolSize.MONGODB_MIN_POOL_SIZE}-{DatabasePoolSize.MONGODB_MAX_POOL_SIZE})")
                
                # Initialize database schema (collections and indexes)
                await self._initialize_schema()
                
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
    
    async def _initialize_schema(self):
        """
        Initialize MongoDB schema: create collections and indexes
        This is idempotent - safe to run multiple times
        """
        try:
            # Get or create 'lines' collection
            collection = self._db[MongoDBCollections.LINES]
            
            # Create indexes for optimal query performance
            
            # Index 1: Compound index on file_id + line_number (unique)
            # Used for: Fast lookup of specific lines in a file
            await collection.create_index(
                [("file_id", 1), ("line_number", 1)],
                unique=True,
                name=MongoDBIndexNames.FILE_LINE_UNIQUE
            )
            
            # Index 2: Descending index on line_length
            # Used for: Fast sorting when getting longest lines across all files
            await collection.create_index(
                [("line_length", -1)],
                name=MongoDBIndexNames.LINE_LENGTH_DESC
            )
            
            # Index 3: Compound index on file_id + line_length (descending)
            # Used for: Fast lookup of longest lines for a specific file
            await collection.create_index(
                [("file_id", 1), ("line_length", -1)],
                name=MongoDBIndexNames.FILE_LENGTH
            )
            
            logger.info("MongoDB schema initialized: collections and indexes created")
            
        except Exception as e:
            # Indexes might already exist - this is fine
            logger.debug(f"MongoDB schema initialization note: {e}")
    
    async def disconnect(self):
        """Close MongoDB client"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")
    
    async def __aenter__(self):
        """Context manager entry"""
        if self._client is None:
            await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Keep connection alive
        pass
    
    @property
    def db(self) -> Optional[AsyncIOMotorDatabase]:
        """Get database instance"""
        return self._db
    
    @property
    def client(self) -> Optional[AsyncIOMotorClient]:
        """Get client instance"""
        return self._client
    
    def get_collection(self, name: str):
        """Get a collection by name"""
        if self._db is None:
            raise RuntimeError("MongoDB not connected")
        return self._db[name]


# Global instance
_mongo_manager = MongoManager()


async def get_mongo() -> MongoManager:
    """Dependency injection for FastAPI"""
    if _mongo_manager._client is None:
        await _mongo_manager.connect()
    return _mongo_manager

