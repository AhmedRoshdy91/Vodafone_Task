"""
Line Service - Business logic for line operations
"""

import random
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException
from app.repositories import FileRepository, LineRepository, CacheRepository
from app.models.schemas import LineResponse, LongestLineResponse
from app.utils import reverse_line
import logging

logger = logging.getLogger(__name__)


class LineService:
    """
    Service for line-related operations
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
    
    async def get_random_line(self, file_id: UUID) -> LineResponse:
        """
        Get a random line from a file
        
        Args:
            file_id: File UUID
            
        Returns:
            LineResponse with line content and metadata
        """
        # Check if file exists
        file_entity = await self.file_repo.get_by_id(file_id)
        if not file_entity:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get random line number
        random_line_num = random.randint(1, file_entity.lines_count)
        
        # Get line from MongoDB
        line_data = await self.line_repo.get_random_line_by_number(
            str(file_id),
            random_line_num
        )
        
        if not line_data:
            raise HTTPException(status_code=404, detail="Line not found")
        
        return LineResponse(
            line=line_data['line_text'],
            line_number=line_data['line_number'],
            filename=file_entity.original_filename,
            most_frequent_letter=line_data.get('most_frequent_letter'),
            frequency=line_data.get('letter_frequency')
        )
    
    async def get_random_line_backwards(self, file_id: UUID) -> LineResponse:
        """
        Get a random line from a file, reversed
        
        Args:
            file_id: File UUID
            
        Returns:
            LineResponse with reversed line content
        """
        line_response = await self.get_random_line(file_id)
        
        # Reverse the line
        line_response.line = reverse_line(line_response.line)
        
        return line_response
    
    async def get_longest_lines_all(self, limit: int = 100) -> List[LongestLineResponse]:
        """
        Get the longest N lines from all files
        
        Args:
            limit: Number of lines to return (default 100)
            
        Returns:
            List of LongestLineResponse
        """
        # Try Redis cache first
        cached_results = await self.cache_repo.get_global_longest(limit)
        
        if cached_results and len(cached_results) >= limit:
            # Cache hit - get full content
            results = []
            
            for member, score in cached_results[:limit]:
                file_id, line_num_str = member.split(':')
                line_num = int(line_num_str)
                
                # Try to get from cache
                cached_line = await self.cache_repo.get_cached_line(file_id, line_num)
                
                if cached_line:
                    results.append(LongestLineResponse(
                        line=cached_line['text'],
                        length=cached_line['length'],
                        line_number=line_num,
                        filename=cached_line.get('filename', 'unknown'),
                        most_frequent_letter=cached_line.get('most_frequent_letter'),
                        frequency=cached_line.get('frequency')
                    ))
                else:
                    # Fallback to MongoDB
                    line_data = await self.line_repo.get_line(file_id, line_num)
                    if line_data:
                        # Get filename from PostgreSQL
                        file_entity = await self.file_repo.get_by_id(UUID(file_id))
                        filename = file_entity.original_filename if file_entity else 'unknown'
                        
                        results.append(LongestLineResponse(
                            line=line_data.line_text,
                            length=line_data.line_length,
                            line_number=line_data.line_number,
                            filename=filename,
                            most_frequent_letter=line_data.most_frequent_letter,
                            frequency=line_data.letter_frequency
                        ))
            
            if len(results) >= limit:
                logger.info(f"Returned {len(results)} longest lines from cache")
                return results[:limit]
        
        # Cache miss - query MongoDB
        mongo_results = await self.line_repo.get_longest_lines_all(limit)
        
        # Get filenames from SQLite (batch query - single DB call)
        file_ids = list(set(doc['file_id'] for doc in mongo_results))
        
        # Fetch all files in a single query
        try:
            file_entities = await self.file_repo.get_by_ids([UUID(fid) for fid in file_ids])
            filenames = {fid: entity.original_filename for fid, entity in file_entities.items()}
            
            # Add 'unknown' for any missing files
            for file_id in file_ids:
                if file_id not in filenames:
                    logger.warning(f"File not found: {file_id}")
                    filenames[file_id] = 'unknown'
        except Exception as e:
            logger.error(f"Error fetching filenames: {e}")
            filenames = {fid: 'unknown' for fid in file_ids}
        
        # Build results
        results = []
        for doc in mongo_results:
            result = LongestLineResponse(
                line=doc['line_text'],
                length=doc['line_length'],
                line_number=doc['line_number'],
                filename=filenames.get(doc['file_id'], 'unknown'),
                most_frequent_letter=doc.get('most_frequent_letter'),
                frequency=doc.get('letter_frequency')
            )
            results.append(result)
            
            # Warm cache
            await self.cache_repo.add_to_global_longest(
                doc['file_id'],
                doc['line_number'],
                doc['line_length']
            )
            
            await self.cache_repo.cache_line_content(
                file_id=doc['file_id'],
                line_number=doc['line_number'],
                line_text=doc['line_text'],
                line_length=doc['line_length'],
                most_frequent_letter=doc.get('most_frequent_letter'),
                letter_frequency=doc.get('letter_frequency'),
                filename=filenames.get(doc['file_id'], 'unknown')
            )
        
        logger.info(f"Returned {len(results)} longest lines from MongoDB")
        return results
    
    async def get_longest_lines_by_file(
        self,
        file_id: UUID,
        limit: int = 20
    ) -> List[LongestLineResponse]:
        """
        Get the longest N lines from a specific file
        
        Args:
            file_id: File UUID
            limit: Number of lines to return (default 20)
            
        Returns:
            List of LongestLineResponse
        """
        # Check if file exists
        file_entity = await self.file_repo.get_by_id(file_id)
        if not file_entity:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Try Redis cache first
        cached_results = await self.cache_repo.get_file_longest(str(file_id), limit)
        
        if cached_results and len(cached_results) >= limit:
            results = []
            
            for line_num_str, score in cached_results[:limit]:
                line_num = int(line_num_str)
                
                # Try to get from cache
                cached_line = await self.cache_repo.get_cached_line(str(file_id), line_num)
                
                if cached_line:
                    results.append(LongestLineResponse(
                        line=cached_line['text'],
                        length=cached_line['length'],
                        line_number=line_num,
                        filename=file_entity.original_filename,
                        most_frequent_letter=cached_line.get('most_frequent_letter'),
                        frequency=cached_line.get('frequency')
                    ))
            
            if len(results) >= limit:
                logger.info(f"Returned {len(results)} longest lines for file {file_id} from cache")
                return results[:limit]
        
        # Fallback to MongoDB
        mongo_results = await self.line_repo.get_longest_lines_by_file(str(file_id), limit)
        
        results = []
        for doc in mongo_results:
            result = LongestLineResponse(
                line=doc['line_text'],
                length=doc['line_length'],
                line_number=doc['line_number'],
                filename=file_entity.original_filename,
                most_frequent_letter=doc.get('most_frequent_letter'),
                frequency=doc.get('letter_frequency')
            )
            results.append(result)
            
            # Warm cache
            await self.cache_repo.add_to_file_longest(
                str(file_id),
                doc['line_number'],
                doc['line_length']
            )
            
            await self.cache_repo.cache_line_content(
                file_id=str(file_id),
                line_number=doc['line_number'],
                line_text=doc['line_text'],
                line_length=doc['line_length'],
                most_frequent_letter=doc.get('most_frequent_letter'),
                letter_frequency=doc.get('letter_frequency'),
                filename=file_entity.original_filename
            )
        
        logger.info(f"Returned {len(results)} longest lines for file {file_id} from MongoDB")
        return results

