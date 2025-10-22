"""
Line Repository - MongoDB operations for line content
"""

from typing import List, Optional
from app.database import MongoManager
from app.models.entities import LineEntity
from app.models.schemas import LineData
import logging

logger = logging.getLogger(__name__)


class LineRepository:
    """
    Repository for line content operations (MongoDB)
    Supports context manager for proper resource management
    """
    
    def __init__(self, mongo: MongoManager):
        self.mongo = mongo
        self.collection = mongo.get_collection('lines')
    
    async def __aenter__(self):
        """Context manager entry - ensure connection is ready"""
        if self.mongo._client is None:
            await self.mongo.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - keep connection alive"""
        # Connection is managed by MongoManager singleton
        # Don't close here, let the application lifecycle handle it
        pass
    
    async def bulk_insert(self, lines: List[LineEntity]) -> int:
        """Bulk insert lines"""
        documents = [line.to_dict() for line in lines]
        
        try:
            result = await self.collection.insert_many(documents, ordered=False)
            count = len(result.inserted_ids)
            logger.info(f"Inserted {count} lines into MongoDB")
            return count
        except Exception as e:
            logger.error(f"Error bulk inserting lines: {e}")
            raise
    
    async def get_line(self, file_id: str, line_number: int) -> Optional[LineData]:
        """Get a specific line"""
        document = await self.collection.find_one({
            'file_id': file_id,
            'line_number': line_number
        })
        
        if not document:
            return None
        
        return LineData(
            file_id=document['file_id'],
            line_number=document['line_number'],
            line_text=document['line_text'],
            line_length=document['line_length'],
            most_frequent_letter=document.get('most_frequent_letter'),
            letter_frequency=document.get('letter_frequency')
        )
    
    async def get_longest_lines_all(self, limit: int = 100) -> List[dict]:
        """Get longest lines across all files"""
        pipeline = [
            {'$sort': {'line_length': -1}},
            {'$limit': limit},
            {'$project': {
                '_id': 0,
                'file_id': 1,
                'line_number': 1,
                'line_text': 1,
                'line_length': 1,
                'most_frequent_letter': 1,
                'letter_frequency': 1
            }}
        ]
        
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        logger.info(f"Retrieved {len(results)} longest lines from all files")
        return results
    
    async def get_longest_lines_by_file(self, file_id: str, limit: int = 20) -> List[dict]:
        """Get longest lines from a specific file"""
        cursor = self.collection.find(
            {'file_id': file_id},
            {'_id': 0}
        ).sort('line_length', -1).limit(limit)
        
        results = await cursor.to_list(length=limit)
        
        logger.info(f"Retrieved {len(results)} longest lines for file {file_id}")
        return results
    
    async def get_random_line_by_number(self, file_id: str, line_number: int) -> Optional[dict]:
        """Get a specific line by its number"""
        document = await self.collection.find_one(
            {'file_id': file_id, 'line_number': line_number},
            {'_id': 0}
        )
        return document
    
    async def delete_by_file(self, file_id: str) -> int:
        """Delete all lines for a file"""
        result = await self.collection.delete_many({'file_id': file_id})
        count = result.deleted_count
        logger.info(f"Deleted {count} lines for file {file_id}")
        return count
    
    async def count_by_file(self, file_id: str) -> int:
        """Count lines for a file"""
        count = await self.collection.count_documents({'file_id': file_id})
        return count

