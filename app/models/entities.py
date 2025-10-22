"""
Database entities and domain models
"""

from datetime import datetime
from typing import Optional, Tuple
from typing_extensions import TypedDict
from uuid import UUID


class FileRow(TypedDict):
    """TypedDict for file table row"""
    id: str
    filename: str
    original_filename: str
    file_size: int
    lines_count: int
    uploaded_at: str
    checksum: Optional[str]
    status: str


class FileEntity:
    """File metadata entity (SQLite)"""
    
    def __init__(
        self,
        id: UUID,
        filename: str,
        original_filename: str,
        file_size: int,
        lines_count: int,
        uploaded_at: datetime,
        checksum: Optional[str] = None,
        status: str = "active"
    ):
        self.id = id
        self.filename = filename
        self.original_filename = original_filename
        self.file_size = file_size
        self.lines_count = lines_count
        self.uploaded_at = uploaded_at
        self.checksum = checksum
        self.status = status
    
    @classmethod
    def from_row(cls, row: Tuple) -> 'FileEntity':
        """
        Create FileEntity from database row tuple
        
        Args:
            row: SQLite row tuple (id, filename, original_filename, file_size, 
                 lines_count, uploaded_at, checksum, status)
        
        Returns:
            FileEntity instance
        """
        return cls(
            id=UUID(row[0]),
            filename=row[1],
            original_filename=row[2],
            file_size=row[3],
            lines_count=row[4],
            uploaded_at=datetime.fromisoformat(row[5]),
            checksum=row[6],
            status=row[7]
        )


class LineEntity:
    """Line content entity (MongoDB)"""
    
    def __init__(
        self,
        file_id: str,
        line_number: int,
        line_text: str,
        line_length: int,
        most_frequent_letter: Optional[str] = None,
        letter_frequency: Optional[int] = None
    ):
        self.file_id = file_id
        self.line_number = line_number
        self.line_text = line_text
        self.line_length = line_length
        self.most_frequent_letter = most_frequent_letter
        self.letter_frequency = letter_frequency
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB"""
        return {
            "file_id": self.file_id,
            "line_number": self.line_number,
            "line_text": self.line_text,
            "line_length": self.line_length,
            "most_frequent_letter": self.most_frequent_letter,
            "letter_frequency": self.letter_frequency,
            "created_at": datetime.utcnow()
        }

