"""
Application Constants and Enums
Centralized location for all magic strings and numbers
"""

from enum import Enum


# ============================================================================
# DATABASE CONSTANTS
# ============================================================================

class DatabasePoolSize:
    """Database connection pool sizes"""
    MONGODB_MAX_POOL_SIZE = 4
    MONGODB_MIN_POOL_SIZE = 1
    REDIS_MAX_CONNECTIONS = 4
    SQLITE_SINGLE_CONNECTION = 1


class DatabaseTimeout:
    """Database timeout values (in seconds)"""
    MONGODB_SERVER_SELECTION = 5
    MONGODB_MAX_IDLE_TIME = 45
    SQLITE_LOCK_TIMEOUT = 30.0
    REDIS_SOCKET_TIMEOUT = 5


# ============================================================================
# FILE STATUS
# ============================================================================

class FileStatus(str, Enum):
    """File status enumeration"""
    ACTIVE = "active"
    DELETED = "deleted"
    PROCESSING = "processing"


# ============================================================================
# FILE UPLOAD CONSTANTS
# ============================================================================

class FileUploadDefaults:
    """Default values for file upload configuration"""
    MAX_FILE_SIZE = 104857600  # 100 MB in bytes
    ALLOWED_EXTENSIONS = ["txt", "csv", "log", "json", "xml"]  # List without dots
    UPLOAD_DIR = "./data/uploads"


class FileSizeUnits:
    """File size units in bytes"""
    BYTE = 1
    KB = 1024
    MB = 1024 * 1024
    GB = 1024 * 1024 * 1024
    
    # Common sizes
    SIZE_5MB = 5 * MB
    SIZE_10MB = 10 * MB
    SIZE_50MB = 50 * MB
    SIZE_100MB = 100 * MB
    SIZE_500MB = 500 * MB
    SIZE_1GB = 1 * GB


# ============================================================================
# CACHE CONSTANTS
# ============================================================================

class CacheDefaults:
    """Redis cache configuration defaults"""
    CACHE_TTL = 3600  # 1 hour in seconds
    GLOBAL_LONGEST_CACHE_SIZE = 100  # Top 100 longest lines globally
    PER_FILE_LONGEST_CACHE_SIZE = 20  # Top 20 longest lines per file


class CacheTTL:
    """Cache Time-To-Live values (in seconds)"""
    ONE_MINUTE = 60
    FIVE_MINUTES = 300
    TEN_MINUTES = 600
    THIRTY_MINUTES = 1800
    ONE_HOUR = 3600
    ONE_DAY = 86400
    ONE_WEEK = 604800


# ============================================================================
# REDIS KEY PREFIXES
# ============================================================================

class RedisKeyPrefix:
    """Redis key prefixes for different data types"""
    LONGEST_GLOBAL = "longest:global"
    LONGEST_FILE = "longest:file:"
    LINE_CONTENT = "line:"
    FILE_CACHE = "file:"
    STATS = "stats:"


# ============================================================================
# APPLICATION DEFAULTS
# ============================================================================

class AppDefaults:
    """Application default values"""
    APP_NAME = "File Upload Service"
    APP_VERSION = "1.0.0"
    HOST = "0.0.0.0"
    PORT = 8000
    ENVIRONMENT = "development"


# ============================================================================
# SQLITE PRAGMAS
# ============================================================================

class SQLitePragma:
    """SQLite PRAGMA statements"""
    FOREIGN_KEYS_ON = "PRAGMA foreign_keys = ON"
    JOURNAL_MODE_WAL = "PRAGMA journal_mode = WAL"
    SYNCHRONOUS_NORMAL = "PRAGMA synchronous = NORMAL"
    TEMP_STORE_MEMORY = "PRAGMA temp_store = MEMORY"
    MMAP_SIZE = "PRAGMA mmap_size = 268435456"  # 256MB
    CACHE_SIZE = "PRAGMA cache_size = -64000"  # 64MB


# ============================================================================
# MONGODB CONSTANTS
# ============================================================================

class MongoDBDefaults:
    """MongoDB default values"""
    DEFAULT_PORT = 27017
    DEFAULT_DB = "fileservice"
    AUTH_SOURCE = "admin"


class MongoDBCollections:
    """MongoDB collection names"""
    LINES = "lines"
    FILES_METADATA = "files_metadata"  # Future use


class MongoDBIndexNames:
    """MongoDB index names"""
    FILE_LINE_UNIQUE = "file_line_unique_idx"
    LINE_LENGTH_DESC = "line_length_desc_idx"
    FILE_LENGTH = "file_length_idx"


# ============================================================================
# REDIS CONSTANTS
# ============================================================================

class RedisDefaults:
    """Redis default values"""
    DEFAULT_PORT = 6379
    DEFAULT_DB = 0
    DEFAULT_ENCODING = "utf-8"


# ============================================================================
# HTTP STATUS CODES
# ============================================================================

class HTTPStatusCode:
    """HTTP status codes for API responses"""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    NOT_ACCEPTABLE = 406
    CONFLICT = 409
    PAYLOAD_TOO_LARGE = 413
    UNSUPPORTED_MEDIA_TYPE = 415
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


# ============================================================================
# CONTENT TYPES
# ============================================================================

class ContentType(str, Enum):
    """HTTP Content-Type values"""
    TEXT_PLAIN = "text/plain"
    APPLICATION_JSON = "application/json"
    APPLICATION_XML = "application/xml"
    APPLICATION_WILDCARD = "application/*"


# ============================================================================
# PAGINATION DEFAULTS
# ============================================================================

class PaginationDefaults:
    """Default values for pagination"""
    DEFAULT_LIMIT = 100
    DEFAULT_OFFSET = 0
    MAX_LIMIT = 1000
    LONGEST_LINES_LIMIT = 100
    LONGEST_FILE_LINES_LIMIT = 20


# ============================================================================
# LOGGING
# ============================================================================

class LogLevel:
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ============================================================================
# FILE PROCESSING
# ============================================================================

class FileProcessing:
    """File processing constants"""
    CHUNK_SIZE = 8192  # 8KB chunks for reading files
    LINE_BUFFER_SIZE = 1000  # Buffer size for line processing
    MAX_FILENAME_LENGTH = 255

