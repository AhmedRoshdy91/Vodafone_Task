"""
Plain Text Response Strategy
"""

from fastapi.responses import PlainTextResponse
from .base import ResponseStrategy


class PlainTextStrategy(ResponseStrategy):
    """
    Strategy for formatting responses as text/plain
    Returns only the line content without metadata
    """
    
    def format(self, data: dict) -> PlainTextResponse:
        """
        Format as plain text
        
        Args:
            data: Dictionary with 'line' key
            
        Returns:
            PlainTextResponse with just the line text
        """
        line_text = data.get('line', '')
        
        return PlainTextResponse(
            content=line_text,
            media_type="text/plain"
        )
    
    @property
    def content_type(self) -> str:
        return "text/plain"

