"""
XML Response Strategy
"""

from fastapi.responses import Response
from xml.etree.ElementTree import Element, SubElement, tostring
from .base import ResponseStrategy


class XmlStrategy(ResponseStrategy):
    """
    Strategy for formatting responses as application/xml
    Returns only the line text
    """
    
    def format(self, data: dict) -> Response:
        """
        Format as XML - returns just the line text
        
        Args:
            data: Dictionary with all response data
            
        Returns:
            Response with just the line content in XML
        """
        # Create simple XML with just the line text
        root = Element('line')
        root.text = data.get('line', '')
        
        # Convert to string
        xml_string = tostring(root, encoding='unicode', method='xml')
        
        # Add XML declaration
        xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'
        
        return Response(
            content=xml_content,
            media_type="application/xml"
        )
    
    @property
    def content_type(self) -> str:
        return "application/xml"

