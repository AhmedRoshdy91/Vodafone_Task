"""
Factory for creating response formatters based on Accept header
"""

from typing import Optional
from fastapi import Header, HTTPException
from .base import ResponseStrategy
from .plain_text_strategy import PlainTextStrategy
from .json_strategy import JsonStrategy
from .xml_strategy import XmlStrategy
from .metadata_strategy import MetadataStrategy
import logging

logger = logging.getLogger(__name__)


class ResponseFormatterFactory:
    """
    Factory for creating appropriate response formatter
    based on Accept header (Factory Pattern)
    """
    
    _strategies = {
        "text/plain": PlainTextStrategy,
        "application/json": JsonStrategy,
        "application/xml": XmlStrategy
    }
    
    @classmethod
    def create(cls, accept_header: Optional[str] = None) -> ResponseStrategy:
        """
        Create response strategy based on Accept header
        
        Args:
            accept_header: Accept header value from request
            
        Returns:
            ResponseStrategy instance
            
        Raises:
            HTTPException: If content type is not supported
        """
        # Default to JSON if no Accept header
        if not accept_header:
            logger.debug("No Accept header provided, defaulting to JSON")
            return JsonStrategy()
        
        logger.debug(f"Accept header received: {accept_header}")
        
        # Parse Accept header (handle multiple values)
        accept_types = [
            mime.strip().split(';')[0].lower()
            for mime in accept_header.split(',')
        ]
        
        logger.debug(f"Parsed accept types: {accept_types}")
        
        # Find first supported type
        for accept_type in accept_types:
            # Check for wildcard BEFORE specific types
            if accept_type == 'application/*' or accept_type == '*/*':
                logger.info(f"Matched wildcard: {accept_type} - returning MetadataStrategy")
                return MetadataStrategy()  # Return metadata for wildcards
            
            if accept_type in cls._strategies:
                logger.info(f"Matched specific type: {accept_type}")
                return cls._strategies[accept_type]()
        
        # If no supported type found, raise error
        logger.warning(f"No matching strategy found for: {accept_types}")
        raise HTTPException(
            status_code=406,
            detail=f"Not Acceptable. Supported types: {', '.join(cls._strategies.keys())}, application/*"
        )
    
    @classmethod
    def supported_types(cls) -> list[str]:
        """Return list of supported content types"""
        return list(cls._strategies.keys())


def get_response_formatter(
    accept: Optional[str] = Header(None, include_in_schema=False)
) -> ResponseStrategy:
    """
    Dependency for FastAPI to inject response formatter
    
    Args:
        accept: Accept header from request
        
    Returns:
        ResponseStrategy instance
    """
    return ResponseFormatterFactory.create(accept)

