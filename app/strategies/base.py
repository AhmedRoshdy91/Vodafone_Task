"""
Base Strategy Interface for Response Formatting
"""

from abc import ABC, abstractmethod
from typing import Any


class ResponseStrategy(ABC):
    """
    Abstract base class for response formatting strategies
    """
    
    @abstractmethod
    def format(self, data: dict) -> Any:
        """
        Format response data according to content type
        
        Args:
            data: Dictionary with response data
            
        Returns:
            Formatted response
        """
        pass
    
    @property
    @abstractmethod
    def content_type(self) -> str:
        """Return the content type for this strategy"""
        pass

