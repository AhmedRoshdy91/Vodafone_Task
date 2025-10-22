"""
API Routes - All endpoints
"""

from typing import Optional, Any
from uuid import UUID
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from app.services import FileService, LineService
from app.models.schemas import (
    FileUploadResponse,
    FileMetadataResponse,
    FilesListResponse,
    LongestLinesListResponse,
    LineResponse,
    LongestLineResponse
)
from app.strategies import ResponseStrategy, get_response_formatter
from app.api.dependencies import get_file_service, get_line_service

logger: logging.Logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(prefix="/api/v1", tags=["File Upload Service"])


# File Upload Endpoints

@router.post("/files/upload", response_model=FileUploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    """
    Upload a text file
    
    - **file**: Text file to upload (.txt)
    
    Returns file metadata including ID, filename, line count, and size
    """
    logger.info(f"Uploading file: {file.filename}")
    return await file_service.upload_file(file)


@router.get("/files", response_model=FilesListResponse)
async def list_files(
    limit: int = 100,
    offset: int = 0,
    file_service: FileService = Depends(get_file_service)
):
    """
    List all uploaded files
    
    - **limit**: Maximum number of files to return (default: 100)
    - **offset**: Number of files to skip (default: 0)
    """
    files: list[FileMetadataResponse] = await file_service.list_files(limit=limit, offset=offset)
    return FilesListResponse(files=files, count=len(files))


@router.get("/files/{file_id}", response_model=FileMetadataResponse)
async def get_file(
    file_id: UUID,
    file_service: FileService = Depends(get_file_service)
):
    """
    Get file metadata by ID
    
    - **file_id**: UUID of the file
    """
    return await file_service.get_file_by_id(file_id)


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: UUID,
    file_service: FileService = Depends(get_file_service)
):
    """
    Delete a file and all associated data
    
    - **file_id**: UUID of the file
    """
    deleted: bool = await file_service.delete_file(file_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {"message": "File deleted successfully", "file_id": str(file_id)}


# Line Operations Endpoints

@router.get("/files/{file_id}/lines/random")
async def get_random_line(
    file_id: UUID,
    line_service: LineService = Depends(get_line_service),
    formatter: ResponseStrategy = Depends(get_response_formatter)
):
    """
    Get one random line from a file
    
    Content negotiation via Accept HTTP header:
    - **Accept: text/plain**: Returns only the line text
    - **Accept: application/json**: Returns {"line": "..."} 
    - **Accept: application/xml**: Returns only the line text (as XML)
    - **Accept: application/\***: Returns full metadata (line, line_number, filename, most_frequent_letter)
    
    - **file_id**: UUID of the file
    
    **Note:** In Swagger UI, the Accept header cannot be easily modified. Use cURL or Postman to test different Accept values.
    """
    
    line_response: LineResponse = await line_service.get_random_line(file_id)
    
    # Convert to dict for formatter
    data: dict[str, Any] = {
        'line': line_response.line,
        'line_number': line_response.line_number,
        'filename': line_response.filename,
        'most_frequent_letter': line_response.most_frequent_letter,
        'frequency': line_response.frequency
    }
    
    return formatter.format(data)


@router.get("/files/{file_id}/lines/random/backwards")
async def get_random_line_backwards(
    file_id: UUID,
    line_service: LineService = Depends(get_line_service),
    formatter: ResponseStrategy = Depends(get_response_formatter)
):
    """
    Get one random line from a file, reversed
    
    Content negotiation via Accept HTTP header:
    - **Accept: text/plain**: Returns only the reversed line text
    - **Accept: application/json**: Returns {"line": "..."} with reversed text
    - **Accept: application/xml**: Returns only the reversed line text (as XML)
    - **Accept: application/\***: Returns full metadata (line, line_number, filename, most_frequent_letter)
    
    - **file_id**: UUID of the file
    
    **Note:** In Swagger UI, the Accept header cannot be easily modified. Use cURL or Postman to test different Accept values.
    """
    
    line_response: LineResponse = await line_service.get_random_line_backwards(file_id)
    
    # Convert to dict for formatter
    data: dict[str, Any] = {
        'line': line_response.line,
        'line_number': line_response.line_number,
        'filename': line_response.filename,
        'most_frequent_letter': line_response.most_frequent_letter,
        'frequency': line_response.frequency
    }
    
    return formatter.format(data)


@router.get("/lines/longest", response_model=LongestLinesListResponse)
async def get_longest_lines_all(
    limit: int = 100,
    line_service: LineService = Depends(get_line_service)
):
    """
    Get the longest N lines from all uploaded files
    
    - **limit**: Number of lines to return (default: 100)
    
    Returns list of lines with metadata sorted by length (descending)
    """
    lines: list[LongestLineResponse] = await line_service.get_longest_lines_all(limit=limit)
    return LongestLinesListResponse(lines=lines, count=len(lines))


@router.get("/files/{file_id}/lines/longest", response_model=LongestLinesListResponse)
async def get_longest_lines_by_file(
    file_id: UUID,
    limit: int = 20,
    line_service: LineService = Depends(get_line_service)
):
    """
    Get the longest N lines from a specific file
    
    - **file_id**: UUID of the file
    - **limit**: Number of lines to return (default: 20)
    
    Returns list of lines with metadata sorted by length (descending)
    """
    lines: list[LongestLineResponse] = await line_service.get_longest_lines_by_file(file_id, limit=limit)
    return LongestLinesListResponse(lines=lines, count=len(lines))


# Health Check

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "File Upload Service",
        "version": "1.0.0"
    }

