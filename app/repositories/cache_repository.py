"""
Cache Repository - Redis operations for caching
"""

from typing import List, Optional, Tuple
import json
from app.database import RedisManager
from app.constants import CacheDefaults
from app.repositories.cache_queries import CacheKeys, CacheConfig
import logging

logger = logging.getLogger(__name__)


class CacheRepository:
    """
    Repository for cache operations (Redis)
    Supports context manager for proper resource management
    """
    
    def __init__(self, redis: RedisManager):
        self.redis = redis
        self.ttl = CacheDefaults.CACHE_TTL
        self.global_cache_size = CacheDefaults.GLOBAL_LONGEST_CACHE_SIZE
        self.per_file_cache_size = CacheDefaults.PER_FILE_LONGEST_CACHE_SIZE
    
    async def __aenter__(self):
        """Context manager entry - ensure connection is ready"""
        if self.redis._client is None:
            await self.redis.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - keep connection alive"""
        # Connection is managed by RedisManager singleton
        # Don't close here, let the application lifecycle handle it
        pass
    
    # Longest Lines Cache (Global)
    
    async def add_to_global_longest(self, file_id: str, line_number: int, line_length: int):
        """Add a line to global longest cache"""
        member = CacheKeys.sorted_set_member(file_id, line_number)
        await self.redis.zadd(CacheKeys.LONGEST_GLOBAL, {member: line_length})
    
    async def get_global_longest(self, limit: int = 100) -> List[Tuple[str, float]]:
        """Get top N longest lines from global cache"""
        results = await self.redis.zrevrange(
            CacheKeys.LONGEST_GLOBAL,
            0,
            limit - 1,
            withscores=True
        )
        
        # Parse results - withscores=True returns list of tuples [(member, score), ...]
        parsed = []
        if results:
            # Check format: if first element is tuple, it's already parsed
            if isinstance(results[0], tuple):
                # Already in tuple format [(member, score), ...]
                parsed = [(str(member), float(score)) for member, score in results]
            else:
                # Flat list format [member, score, member, score, ...]
                for i in range(0, len(results), 2):
                    member = str(results[i])
                    score = float(results[i + 1])
                    parsed.append((member, score))
        
        return parsed
    
    async def trim_global_longest(self):
        """Keep only top N in global cache"""
        await self.redis.zremrangebyrank(
            CacheKeys.LONGEST_GLOBAL,
            0,
            -(self.global_cache_size + 1)
        )
    
    # Per-File Longest Lines Cache
    
    async def add_to_file_longest(self, file_id: str, line_number: int, line_length: int):
        """Add a line to per-file longest cache"""
        key = CacheKeys.longest_file_key(file_id)
        await self.redis.zadd(key, {str(line_number): line_length})
    
    async def get_file_longest(self, file_id: str, limit: int = 20) -> List[Tuple[str, float]]:
        """Get top N longest lines for a file"""
        key = CacheKeys.longest_file_key(file_id)
        results = await self.redis.zrevrange(key, 0, limit - 1, withscores=True)
        
        # Parse results - withscores=True returns list of tuples [(member, score), ...]
        parsed = []
        if results:
            # Check format: if first element is tuple, it's already parsed
            if isinstance(results[0], tuple):
                # Already in tuple format [(line_num, score), ...]
                parsed = [(str(line_num), float(score)) for line_num, score in results]
            else:
                # Flat list format [line_num, score, line_num, score, ...]
                for i in range(0, len(results), 2):
                    line_num = str(results[i])
                    score = float(results[i + 1])
                    parsed.append((line_num, score))
        
        return parsed
    
    async def trim_file_longest(self, file_id: str):
        """Keep only top N in per-file cache"""
        key = CacheKeys.longest_file_key(file_id)
        await self.redis.zremrangebyrank(key, 0, -(self.per_file_cache_size + 1))
    
    # Line Content Cache
    
    async def cache_line_content(
        self,
        file_id: str,
        line_number: int,
        line_text: str,
        line_length: int,
        most_frequent_letter: Optional[str] = None,
        letter_frequency: Optional[int] = None,
        filename: Optional[str] = None
    ):
        """Cache line content with metadata"""
        key = CacheKeys.line_content_key(file_id, line_number)
        value = json.dumps({
            'text': line_text,
            'length': line_length,
            'most_frequent_letter': most_frequent_letter,
            'frequency': letter_frequency,
            'filename': filename
        })
        await self.redis.set(key, value, ex=self.ttl)
    
    async def get_cached_line(self, file_id: str, line_number: int) -> Optional[dict]:
        """Get cached line content"""
        key = CacheKeys.line_content_key(file_id, line_number)
        cached = await self.redis.get(key)
        
        if cached:
            return json.loads(cached)
        
        return None
    
    async def delete_file_cache(self, file_id: str):
        """Delete all cache entries for a file"""
        # Delete per-file longest
        file_key = CacheKeys.longest_file_key(file_id)
        await self.redis.delete(file_key)
        
        # Note: We can't easily delete all line:{file_id}:* keys without SCAN
        # In production, you'd use SCAN to find and delete them
        logger.info(f"Deleted cache entries for file {file_id}")
    
    async def clear_all_cache(self):
        """Clear all caches (use with caution)"""
        # In production, implement proper cache clearing
        logger.warning("Clear all cache called - implement with SCAN in production")

