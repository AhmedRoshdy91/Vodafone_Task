"""
Redis Connection Manager with Context Manager Pattern
"""

import redis.asyncio as redis
from typing import Optional
from app.config import settings
from app.constants import RedisDefaults, DatabasePoolSize
import logging

logger = logging.getLogger(__name__)


class RedisManager:
    """
    Singleton Redis connection manager with context manager support
    Uses connection pooling with max_connections limit
    """
    
    _instance: Optional['RedisManager'] = None
    _client: Optional[redis.Redis] = None
    _pool: Optional[redis.ConnectionPool] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Initialize Redis client with connection pool"""
        if self._client is None:
            try:
                # Create connection pool with max_connections limit
                self._pool = redis.ConnectionPool.from_url(
                    settings.redis_url,
                    encoding=RedisDefaults.DEFAULT_ENCODING,
                    decode_responses=True,
                    max_connections=DatabasePoolSize.REDIS_MAX_CONNECTIONS
                )
                
                # Create client with connection pool
                self._client = redis.Redis(connection_pool=self._pool)
                
                # Test connection
                await self._client.ping()
                logger.info(f"Redis connection established (max pool size: {DatabasePoolSize.REDIS_MAX_CONNECTIONS})")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
    
    async def disconnect(self):
        """Close Redis client and connection pool"""
        if self._client:
            await self._client.close()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        logger.info("Redis connection closed")
    
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
    def client(self) -> Optional[redis.Redis]:
        """Get Redis client"""
        return self._client
    
    async def set(self, key: str, value: str, ex: Optional[int] = None):
        """Set a key-value pair"""
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return await self._client.set(key, value, ex=ex)
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key"""
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return await self._client.get(key)
    
    async def delete(self, *keys: str):
        """Delete one or more keys"""
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return await self._client.delete(*keys)
    
    async def zadd(self, key: str, mapping: dict, **kwargs):
        """Add to sorted set"""
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return await self._client.zadd(key, mapping, **kwargs)
    
    async def zrevrange(self, key: str, start: int, end: int, withscores: bool = False):
        """Get range from sorted set (descending)"""
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return await self._client.zrevrange(key, start, end, withscores=withscores)
    
    async def zremrangebyrank(self, key: str, start: int, end: int):
        """Remove range from sorted set by rank"""
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return await self._client.zremrangebyrank(key, start, end)


# Global instance
_redis_manager = RedisManager()


async def get_redis() -> RedisManager:
    """Dependency injection for FastAPI"""
    if _redis_manager._client is None:
        await _redis_manager.connect()
    return _redis_manager

