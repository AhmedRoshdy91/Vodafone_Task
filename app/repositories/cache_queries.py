"""
Redis Key Constants and Cache Configuration
All Redis keys and cache-related constants are defined here

Note: Some constants have been moved to app/constants.py for centralization
"""

from app.constants import RedisKeyPrefix, CacheDefaults


class CacheKeys:
    """Redis key patterns for caching"""
    
    # Import from constants for consistency
    LONGEST_GLOBAL = RedisKeyPrefix.LONGEST_GLOBAL
    LONGEST_FILE_PREFIX = RedisKeyPrefix.LONGEST_FILE
    LINE_CONTENT_PREFIX = RedisKeyPrefix.LINE_CONTENT
    
    @staticmethod
    def longest_file_key(file_id: str) -> str:
        """Generate key for per-file longest lines"""
        return f"{CacheKeys.LONGEST_FILE_PREFIX}{file_id}"
    
    @staticmethod
    def line_content_key(file_id: str, line_number: int) -> str:
        """Generate key for line content cache"""
        return f"{CacheKeys.LINE_CONTENT_PREFIX}{file_id}:{line_number}"
    
    @staticmethod
    def sorted_set_member(file_id: str, line_number: int) -> str:
        """Generate member for sorted set"""
        return f"{file_id}:{line_number}"


class CacheConfig:
    """Cache configuration constants"""
    
    # Import from constants for consistency
    DEFAULT_TTL = CacheDefaults.CACHE_TTL
    DEFAULT_GLOBAL_CACHE_SIZE = CacheDefaults.GLOBAL_LONGEST_CACHE_SIZE
    DEFAULT_PER_FILE_CACHE_SIZE = CacheDefaults.PER_FILE_LONGEST_CACHE_SIZE

