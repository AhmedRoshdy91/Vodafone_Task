"""
FastAPI Main Application
File Upload Service with SQLite + MongoDB + Redis
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import logging.handlers
import os
from pathlib import Path

from app.config import settings
from app.database import SQLiteManager, MongoManager, RedisManager
from app.api import router

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
log_level = logging.INFO if settings.debug else logging.WARNING
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Create formatters and handlers
formatter = logging.Formatter(log_format)

# Console handler (stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(formatter)

# File handler with rotation (max 10MB per file, keep 5 backup files)
file_handler = logging.handlers.RotatingFileHandler(
    filename='logs/app.log',
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(log_level)
file_handler.setFormatter(formatter)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(log_level)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("Starting File Upload Service...")
    
    # Initialize database connections
    sqlite = SQLiteManager()
    mongo = MongoManager()
    redis = RedisManager()
    
    try:
        await sqlite.connect()
        logger.info("✓ SQLite connected")
    except Exception as e:
        logger.error(f"✗ SQLite connection failed: {e}")
        raise
    
    try:
        await mongo.connect()
        logger.info("✓ MongoDB connected")
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {e}")
        raise
    
    try:
        await redis.connect()
        logger.info("✓ Redis connected")
    except Exception as e:
        logger.error(f"✗ Redis connection failed: {e}")
        raise
    
    logger.info("🚀 File Upload Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down File Upload Service...")
    
    await sqlite.disconnect()
    logger.info("✓ SQLite disconnected")
    
    await mongo.disconnect()
    logger.info("✓ MongoDB disconnected")
    
    await redis.disconnect()
    logger.info("✓ Redis disconnected")
    
    logger.info("👋 File Upload Service stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    File Upload Service with advanced architecture:
    - SQLite for metadata
    - MongoDB for line content
    - Redis for caching
    
    ## Features
    - Upload text files
    - Get random lines from files
    - Get random lines backwards
    - Get longest 100 lines from all files
    - Get longest 20 lines from a specific file
    - Content negotiation (text/plain, JSON, XML)
    
    ## Architecture Patterns
    - Repository Pattern
    - Service Layer Pattern
    - Strategy Pattern (Content Negotiation)
    - Factory Pattern
    - Singleton Pattern (Database Connections)
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
            "path": str(request.url)
        }
    )


# Include routers
app.include_router(router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

