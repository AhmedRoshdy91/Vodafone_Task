"""
File Repository - SQLite operations for file metadata
"""

from typing import List, Optional
from uuid import UUID
from app.database import SQLiteManager
from app.models.entities import FileEntity
from app.repositories.queries import FileQueries
from app.constants import FileStatus, PaginationDefaults
import logging

logger = logging.getLogger(__name__)


class FileRepository:
    """
    Repository for file metadata operations (SQLite)
    Supports context manager for proper resource management
    """
    
    def __init__(self, sqlite: SQLiteManager):
        self.sqlite = sqlite
    
    async def __aenter__(self):
        """Context manager entry - ensure connection is ready"""
        if self.sqlite._connection is None:
            await self.sqlite.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - keep connection alive"""
        # Connection is managed by SQLiteManager singleton
        # Don't close here, let the application lifecycle handle it
        pass
    
    async def create(
        self,
        file_id: UUID,
        filename: str,
        original_filename: str,
        file_size: int,
        lines_count: int,
        checksum: Optional[str] = None
    ) -> FileEntity:
        """Create a new file record"""
        await self.sqlite.execute(
            FileQueries.INSERT_FILE,
            str(file_id),
            filename,
            original_filename,
            file_size,
            lines_count,
            checksum,
            FileStatus.ACTIVE
        )
        
        # Fetch the created record
        row = await self.sqlite.fetchone(
            FileQueries.SELECT_FILE_BY_ID,
            str(file_id),
            FileStatus.ACTIVE
        )
        
        logger.info(f"Created file record: {file_id}")
        
        return FileEntity.from_row(row)
    
    async def get_by_id(self, file_id: UUID) -> Optional[FileEntity]:
        """Get file by ID"""
        row = await self.sqlite.fetchone(
            FileQueries.SELECT_FILE_BY_ID,
            str(file_id),
            FileStatus.ACTIVE
        )
        
        if not row:
            return None
        
        return FileEntity.from_row(row)
    
    async def get_by_ids(self, file_ids: List[UUID]) -> dict[str, FileEntity]:
        """
        Get multiple files by IDs in a single query
        Returns a dictionary mapping file_id (as string) to FileEntity
        """
        if not file_ids:
            return {}
        
        # Convert UUIDs to strings
        file_id_strs = [str(file_id) for file_id in file_ids]
        
        # Create placeholders for SQL IN clause
        placeholders = ','.join('?' * len(file_id_strs))
        query = FileQueries.SELECT_FILES_BY_IDS.format(placeholders)
        
        # Execute query with all file IDs and status
        rows = await self.sqlite.fetch(query, *file_id_strs, FileStatus.ACTIVE)
        
        # Build dictionary mapping file_id to entity
        result = {}
        for row in rows:
            entity = FileEntity.from_row(row)
            result[str(entity.id)] = entity
        
        return result
    
    async def get_all(
        self,
        limit: int = PaginationDefaults.DEFAULT_LIMIT,
        offset: int = PaginationDefaults.DEFAULT_OFFSET
    ) -> List[FileEntity]:
        """Get all files with pagination"""
        rows = await self.sqlite.fetch(
            FileQueries.SELECT_ALL_FILES,
            FileStatus.ACTIVE,
            limit,
            offset
        )
        
        return [FileEntity.from_row(row) for row in rows]
    
    async def delete(self, file_id: UUID) -> bool:
        """Soft delete a file"""
        cursor = await self.sqlite.execute(
            FileQueries.SOFT_DELETE_FILE,
            FileStatus.DELETED,
            str(file_id),
            FileStatus.ACTIVE
        )
        
        if cursor.rowcount > 0:
            logger.info(f"Deleted file: {file_id}")
            return True
        
        return False
    
    async def exists(self, file_id: UUID) -> bool:
        """Check if file exists"""
        result = await self.sqlite.fetchval(
            FileQueries.SELECT_FILE_EXISTS,
            str(file_id),
            FileStatus.ACTIVE
        )
        return result is not None
    
    async def get_lines_count(self, file_id: UUID) -> Optional[int]:
        """Get number of lines in a file"""
        return await self.sqlite.fetchval(
            FileQueries.SELECT_LINES_COUNT,
            str(file_id),
            FileStatus.ACTIVE
        )

