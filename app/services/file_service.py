"""
File Service - Business logic for file operations
"""

import random
from uuid import UUID, uuid4
from typing import List
from fastapi import UploadFile, HTTPException
from app.repositories import FileRepository, LineRepository, CacheRepository
from app.models.entities import LineEntity
from app.utils import (
    validate_file_extension,
    validate_file_size,
    secure_filename,
    FileProcessor,
    find_most_frequent_letter
)
from app.models.schemas import FileUploadResponse, FileMetadataResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class FileService:
    """
    Service for file upload and management operations
    """
    
    def __init__(
        self,
        file_repo: FileRepository,
        line_repo: LineRepository,
        cache_repo: CacheRepository
    ):
        self.file_repo = file_repo
        self.line_repo = line_repo
        self.cache_repo = cache_repo
        self.file_processor = FileProcessor()
    
    async def upload_file(self, file: UploadFile) -> FileUploadResponse:
        """
        Handle file upload with full processing pipeline
        
        Args:
            file: Uploaded file
            
        Returns:
            FileUploadResponse with file metadata
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate file extension
        if not validate_file_extension(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Only text files are accepted."
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if not validate_file_size(len(content)):
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_file_size} bytes."
            )
        
        # Generate file ID and secure filename
        file_id = uuid4()
        safe_filename = secure_filename(file.filename)
        stored_filename = f"{file_id}_{safe_filename}"
        
        # Save file to disk
        file_path = await self.file_processor.save_upload_file(content, stored_filename)
        
        # Calculate checksum
        checksum = await self.file_processor.calculate_checksum(file_path)
        
        # Process file line by line
        lines_data = []
        line_entities = []
        
        async for line_num, line_text in self.file_processor.read_lines(file_path):
            length = len(line_text)
            most_freq, freq = find_most_frequent_letter(line_text)
            
            # Create line entity
            line_entity = LineEntity(
                file_id=str(file_id),
                line_number=line_num,
                line_text=line_text,
                line_length=length,
                most_frequent_letter=most_freq,
                letter_frequency=freq
            )
            line_entities.append(line_entity)
            
            # Store data for caching
            lines_data.append({
                'file_id': str(file_id),
                'line_number': line_num,
                'line_text': line_text,
                'line_length': length,
                'most_frequent_letter': most_freq,
                'letter_frequency': freq
            })
        
        lines_count = len(line_entities)
        file_size = len(content)
        
        # Save to PostgreSQL (metadata)
        await self.file_repo.create(
            file_id=file_id,
            filename=stored_filename,
            original_filename=file.filename,
            file_size=file_size,
            lines_count=lines_count,
            checksum=checksum
        )
        
        logger.info(f"Created file metadata in PostgreSQL: {file_id}")
        
        # Save to MongoDB (line content) - bulk insert
        if line_entities:
            await self.line_repo.bulk_insert(line_entities)
            logger.info(f"Inserted {len(line_entities)} lines into MongoDB")
        
        # Update Redis cache (only longest lines)
        await self._update_cache(str(file_id), lines_data, file.filename)
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            lines_count=lines_count,
            file_size=file_size,
            status="success"
        )
    
    async def _update_cache(self, file_id: str, lines_data: List[dict], filename: str):
        """
        Update Redis cache with longest lines
        
        Args:
            file_id: File UUID
            lines_data: List of line data dictionaries
            filename: Original filename
        """
        # Sort by length and get longest N lines
        longest_lines = sorted(
            lines_data,
            key=lambda x: x['line_length'],
            reverse=True
        )[:100]  # Cache top 100 from this file
        
        for line in longest_lines:
            # Add to global longest cache
            await self.cache_repo.add_to_global_longest(
                file_id,
                line['line_number'],
                line['line_length']
            )
            
            # Add to per-file longest cache
            await self.cache_repo.add_to_file_longest(
                file_id,
                line['line_number'],
                line['line_length']
            )
            
            # Cache line content
            await self.cache_repo.cache_line_content(
                file_id=file_id,
                line_number=line['line_number'],
                line_text=line['line_text'],
                line_length=line['line_length'],
                most_frequent_letter=line.get('most_frequent_letter'),
                letter_frequency=line.get('letter_frequency'),
                filename=filename
            )
        
        # Trim caches to maintain size limits
        await self.cache_repo.trim_global_longest()
        await self.cache_repo.trim_file_longest(file_id)
        
        logger.info(f"Updated cache for file {file_id}")
    
    async def get_file_by_id(self, file_id: UUID) -> FileMetadataResponse:
        """Get file metadata by ID"""
        file_entity = await self.file_repo.get_by_id(file_id)
        
        if not file_entity:
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileMetadataResponse(
            id=file_entity.id,
            filename=file_entity.filename,
            original_filename=file_entity.original_filename,
            file_size=file_entity.file_size,
            lines_count=file_entity.lines_count,
            uploaded_at=file_entity.uploaded_at,
            status=file_entity.status
        )
    
    async def list_files(self, limit: int = 100, offset: int = 0) -> List[FileMetadataResponse]:
        """List all files with pagination"""
        file_entities = await self.file_repo.get_all(limit=limit, offset=offset)
        
        return [
            FileMetadataResponse(
                id=entity.id,
                filename=entity.filename,
                original_filename=entity.original_filename,
                file_size=entity.file_size,
                lines_count=entity.lines_count,
                uploaded_at=entity.uploaded_at,
                status=entity.status
            )
            for entity in file_entities
        ]
    
    async def delete_file(self, file_id: UUID) -> bool:
        """
        Delete a file and all associated data
        
        Args:
            file_id: File UUID
            
        Returns:
            True if deleted successfully
        """
        # Delete from PostgreSQL
        deleted = await self.file_repo.delete(file_id)
        
        if not deleted:
            return False
        
        # Delete from MongoDB
        await self.line_repo.delete_by_file(str(file_id))
        
        # Delete from Redis cache
        await self.cache_repo.delete_file_cache(str(file_id))
        
        logger.info(f"Deleted file {file_id} from all databases")
        
        return True

