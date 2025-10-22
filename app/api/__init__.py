"""
API Layer - Routes and Dependencies
"""

from .dependencies import get_file_service, get_line_service
from .routes import router

__all__ = ["router", "get_file_service", "get_line_service"]

