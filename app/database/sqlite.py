"""
SQLite Connection Manager with Context Manager Pattern
"""

import aiosqlite
from typing import Optional
from app.config import settings
from app.constants import DatabaseTimeout, SQLitePragma
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLiteManager:
    """
    Singleton SQLite connection manager with context manager support
    """
    
    _instance: Optional['SQLiteManager'] = None
    _connection: Optional[aiosqlite.Connection] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Initialize SQLite connection"""
        if self._connection is None:
            try:
                # Ensure directory exists
                db_path = Path(settings.sqlite_db_path)
                db_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create connection
                self._connection = await aiosqlite.connect(
                    settings.sqlite_db_path,
                    timeout=DatabaseTimeout.SQLITE_LOCK_TIMEOUT,
                    check_same_thread=False
                )
                
                # Enable foreign keys
                await self._connection.execute(SQLitePragma.FOREIGN_KEYS_ON)
                
                # Enable WAL mode for better concurrency
                await self._connection.execute(SQLitePragma.JOURNAL_MODE_WAL)
                
                # Create tables if they don't exist
                await self._create_tables()
                
                logger.info(f"SQLite connection established: {settings.sqlite_db_path}")
            except Exception as e:
                logger.error(f"Failed to connect to SQLite: {e}")
                raise
    
    async def _create_tables(self):
        """Create tables if they don't exist"""
        create_files_table = """
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            original_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            lines_count INTEGER NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum TEXT,
            status TEXT DEFAULT 'active',
            CHECK (status IN ('active', 'deleted', 'processing'))
        )
        """
        
        create_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_files_uploaded_at ON files(uploaded_at)",
            "CREATE INDEX IF NOT EXISTS idx_files_status ON files(status)",
            "CREATE INDEX IF NOT EXISTS idx_files_filename ON files(filename)"
        ]
        
        await self._connection.execute(create_files_table)
        for index_sql in create_indexes:
            await self._connection.execute(index_sql)
        
        await self._connection.commit()
        logger.info("SQLite tables and indexes created")
    
    async def disconnect(self):
        """Close SQLite connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("SQLite connection closed")
    
    async def __aenter__(self):
        """Context manager entry"""
        if self._connection is None:
            await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        # Keep connection alive, don't close on every context exit
        pass
    
    async def execute(self, query: str, *args):
        """Execute a query"""
        if self._connection is None:
            await self.connect()
        
        cursor = await self._connection.execute(query, args)
        await self._connection.commit()
        return cursor
    
    async def executemany(self, query: str, params_list):
        """Execute many queries"""
        if self._connection is None:
            await self.connect()
        
        await self._connection.executemany(query, params_list)
        await self._connection.commit()
    
    async def fetch(self, query: str, *args):
        """Fetch multiple rows"""
        if self._connection is None:
            await self.connect()
        
        cursor = await self._connection.execute(query, args)
        rows = await cursor.fetchall()
        return rows
    
    async def fetchone(self, query: str, *args):
        """Fetch a single row"""
        if self._connection is None:
            await self.connect()
        
        cursor = await self._connection.execute(query, args)
        row = await cursor.fetchone()
        return row
    
    async def fetchval(self, query: str, *args):
        """Fetch a single value"""
        if self._connection is None:
            await self.connect()
        
        cursor = await self._connection.execute(query, args)
        row = await cursor.fetchone()
        return row[0] if row else None
    
    @property
    def connection(self) -> Optional[aiosqlite.Connection]:
        """Get the connection"""
        return self._connection


# Global instance
_sqlite_manager = SQLiteManager()


async def get_sqlite() -> SQLiteManager:
    """Dependency injection for FastAPI"""
    if _sqlite_manager._connection is None:
        await _sqlite_manager.connect()
    return _sqlite_manager

