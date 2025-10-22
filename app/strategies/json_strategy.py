"""
JSON Response Strategy
"""

from fastapi.responses import JSONResponse
from app.models.schemas import LineOnlyResponse
from .base import ResponseStrategy


class JsonStrategy(ResponseStrategy):
    """
    Strategy for formatting responses as application/json
    Returns line text wrapped in an object: {"line": "..."}
    """
    
    def format(self, data: dict) -> JSONResponse:
        """
        Format as JSON - returns line text wrapped in an object
        
        Args:
            data: Dictionary with all response data
            
        Returns:
            JSONResponse with line wrapped in object
        """
        # Create typed response
        response_data: LineOnlyResponse = {
            "line": data.get('line', '')
        }
        
        return JSONResponse(
            content=response_data,
            media_type="application/json"
        )
    
    @property
    def content_type(self) -> str:
        return "application/json"

