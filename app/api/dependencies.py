"""
Dependency Injection for FastAPI
"""

from app.database import get_sqlite, get_mongo, get_redis
from app.repositories import FileRepository, LineRepository, CacheRepository
from app.services import FileService, LineService


async def get_file_service() -> FileService:
    """
    Dependency injection for FileService
    """
    sqlite = await get_sqlite()
    mongo = await get_mongo()
    redis = await get_redis()
    
    file_repo = FileRepository(sqlite)
    line_repo = LineRepository(mongo)
    cache_repo = CacheRepository(redis)
    
    return FileService(file_repo, line_repo, cache_repo)


async def get_line_service() -> LineService:
    """
    Dependency injection for LineService
    """
    sqlite = await get_sqlite()
    mongo = await get_mongo()
    redis = await get_redis()
    
    file_repo = FileRepository(sqlite)
    line_repo = LineRepository(mongo)
    cache_repo = CacheRepository(redis)
    
    return LineService(file_repo, line_repo, cache_repo)

