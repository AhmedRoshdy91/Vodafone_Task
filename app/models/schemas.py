"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, TypedDict
from uuid import UUID
from pydantic import BaseModel, Field, validator


# TypedDict for response formatting

class LineOnlyResponse(TypedDict):
    """Response containing only the line text"""
    line: str


class LineMetadataResponse(TypedDict):
    """Response containing line with full metadata"""
    line: str
    line_number: int
    filename: str
    most_frequent_letter: Optional[str]


# Request Schemas

class FileUploadResponse(BaseModel):
    """Response after file upload"""
    file_id: UUID
    filename: str
    lines_count: int
    file_size: int
    status: str = "success"
    
    class Config:
        from_attributes = True


# Response Schemas

class LineResponse(BaseModel):
    """Single line response"""
    line: str
    line_number: int
    filename: str
    most_frequent_letter: Optional[str] = None
    frequency: Optional[int] = None


class LineResponsePlain(BaseModel):
    """Plain text response (just the line)"""
    content: str


class LongestLineResponse(BaseModel):
    """Response for longest lines query"""
    line: str
    length: int
    line_number: int
    filename: str
    most_frequent_letter: Optional[str] = None
    frequency: Optional[int] = None
    
    @validator('frequency', pre=True)
    def validate_frequency(cls, v):
        """Handle frequency validation - convert tuple to int if needed"""
        if v is None:
            return None
        if isinstance(v, tuple):
            # If it's a tuple, take the second element (frequency value)
            return v[1] if len(v) > 1 else 0
        if isinstance(v, (int, float)):
            return int(v)
        return None
    
    @validator('most_frequent_letter', pre=True)
    def validate_letter(cls, v):
        """Handle most_frequent_letter validation - extract from tuple if needed"""
        if v is None:
            return None
        if isinstance(v, tuple):
            # If it's a tuple, take the first element (letter value)
            return v[0] if len(v) > 0 else None
        if isinstance(v, str):
            return v
        return None


class LongestLinesListResponse(BaseModel):
    """List of longest lines"""
    lines: list[LongestLineResponse]
    count: int


class FileMetadataResponse(BaseModel):
    """File metadata response"""
    id: UUID
    filename: str
    original_filename: str
    file_size: int
    lines_count: int
    uploaded_at: datetime
    status: str
    
    class Config:
        from_attributes = True


class FilesListResponse(BaseModel):
    """List of files response"""
    files: list[FileMetadataResponse]
    count: int


# Internal Data Transfer Objects

class LineData(BaseModel):
    """Internal DTO for line processing"""
    file_id: str
    line_number: int
    line_text: str
    line_length: int
    most_frequent_letter: Optional[str] = None
    letter_frequency: Optional[int] = None


class LineMetadata(BaseModel):
    """Line metadata for caching"""
    text: str
    length: int
    most_frequent_letter: Optional[str] = None
    frequency: Optional[int] = None
    filename: Optional[str] = None


# Error Responses

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    status_code: int


# Export list
__all__ = [
    # TypedDicts for response formatting
    "LineOnlyResponse",
    "LineMetadataResponse",
    # Pydantic models
    "FileUploadResponse",
    "LineResponse",
    "LineResponsePlain",
    "LongestLineResponse",
    "LongestLinesListResponse",
    "FileMetadataResponse",
    "FilesListResponse",
    "LineData",
    "LineMetadata",
    "ErrorResponse",
]

