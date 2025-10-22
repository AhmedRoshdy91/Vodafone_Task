"""
Metadata Response Strategy for application/* wildcard
"""

from fastapi.responses import JSONResponse
from app.models.schemas import LineMetadataResponse
from .base import ResponseStrategy


class MetadataStrategy(ResponseStrategy):
    """
    Strategy for formatting responses as application/* (wildcard)
    Returns full metadata: line, line_number, filename, most_frequent_letter
    """
    
    def format(self, data: dict) -> JSONResponse:
        """
        Format with full metadata
        
        Args:
            data: Dictionary with all response data
            
        Returns:
            JSONResponse with complete metadata
        """
        # Create typed response
        response_data: LineMetadataResponse = {
            "line": data.get('line', ''),
            "line_number": data.get('line_number'),
            "filename": data.get('filename', 'unknown'),
            "most_frequent_letter": data.get('most_frequent_letter')
        }
        
        return JSONResponse(
            content=response_data,
            media_type="application/json"
        )
    
    @property
    def content_type(self) -> str:
        return "application/*"

