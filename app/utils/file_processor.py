"""
File processing utilities
"""

import os
import hashlib
import aiofiles
from typing import AsyncGenerator, Tuple
from pathlib import Path
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class FileProcessor:
    """
    Utility class for file processing operations
    """
    
    @staticmethod
    async def save_upload_file(file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk
        
        Args:
            file_content: File content as bytes
            filename: Filename
            
        Returns:
            Path to saved file
        """
        # Ensure upload directory exists
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Build file path
        file_path = upload_dir / filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        logger.info(f"Saved file to {file_path}")
        return str(file_path)
    
    @staticmethod
    async def read_lines(file_path: str) -> AsyncGenerator[Tuple[int, str], None]:
        """
        Read file line by line asynchronously
        
        Args:
            file_path: Path to file
            
        Yields:
            Tuple of (line_number, line_text)
        """
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            line_number = 1
            async for line in f:
                yield line_number, line.rstrip('\n')
                line_number += 1
    
    @staticmethod
    async def calculate_checksum(file_path: str) -> str:
        """
        Calculate SHA256 checksum of a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of checksum
        """
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    async def get_file_size(file_path: str) -> int:
        """
        Get file size in bytes
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        return os.path.getsize(file_path)
    
    @staticmethod
    async def delete_file(file_path: str) -> bool:
        """
        Delete a file from disk
        
        Args:
            file_path: Path to file
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
        
        return False
    
    @staticmethod
    async def read_specific_line(file_path: str, line_number: int) -> str:
        """
        Read a specific line from a file
        
        Args:
            file_path: Path to file
            line_number: Line number (1-based)
            
        Returns:
            Line content
        """
        current_line = 1
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            async for line in f:
                if current_line == line_number:
                    return line.rstrip('\n')
                current_line += 1
        
        return ""

