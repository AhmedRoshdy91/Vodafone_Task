"""
Application Configuration using Pydantic Settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from app.constants import (
    AppDefaults,
    DatabasePoolSize,
    FileUploadDefaults,
    CacheDefaults,
    MongoDBDefaults,
    RedisDefaults
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = Field(default=AppDefaults.APP_NAME, alias="APP_NAME")
    app_version: str = Field(default=AppDefaults.APP_VERSION, alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default=AppDefaults.ENVIRONMENT, alias="ENVIRONMENT")
    
    # Server
    host: str = Field(default=AppDefaults.HOST, alias="HOST")
    port: int = Field(default=AppDefaults.PORT, alias="PORT")
    
    # SQLite
    sqlite_db_path: str = Field(default="./data/fileservice.db", alias="SQLITE_DB_PATH")
    
    # MongoDB (runtime configuration only)
    mongo_host: str = Field(alias="MONGO_HOST")
    mongo_port: int = Field(default=MongoDBDefaults.DEFAULT_PORT, alias="MONGO_PORT")
    mongo_db: str = Field(default=MongoDBDefaults.DEFAULT_DB, alias="MONGO_DB")
    mongo_user: str = Field(alias="MONGO_USER")
    mongo_password: str = Field(alias="MONGO_PASSWORD")
    
    # Redis (runtime configuration only)
    redis_host: str = Field(alias="REDIS_HOST")
    redis_port: int = Field(default=RedisDefaults.DEFAULT_PORT, alias="REDIS_PORT")
    redis_password: str = Field(alias="REDIS_PASSWORD")
    redis_db: int = Field(default=RedisDefaults.DEFAULT_DB, alias="REDIS_DB")
    
    # File Upload (runtime configuration only - upload directory)
    upload_dir: str = Field(default=FileUploadDefaults.UPLOAD_DIR, alias="UPLOAD_DIR")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def mongo_dsn(self) -> str:
        """Build MongoDB connection string"""
        return f"mongodb://{self.mongo_user}:{self.mongo_password}@{self.mongo_host}:{self.mongo_port}/{self.mongo_db}?authSource={MongoDBDefaults.AUTH_SOURCE}"
    
    @property
    def redis_url(self) -> str:
        """Build Redis connection URL"""
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"


# Global settings instance
settings = Settings()

