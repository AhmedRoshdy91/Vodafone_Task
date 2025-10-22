"""
Validation utilities
"""

import re
from pathlib import Path
from app.constants import FileUploadDefaults


def validate_file_extension(filename: str) -> bool:
    """
    Validate if file extension is allowed
    
    Args:
        filename: Name of the file
        
    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename:
        return False
    
    ext = Path(filename).suffix.lstrip('.').lower()
    allowed = FileUploadDefaults.ALLOWED_EXTENSIONS
    
    return ext in allowed


def secure_filename(filename: str) -> str:
    """
    Make a filename safe for filesystem
    
    Args:
        filename: Original filename
        
    Returns:
        Secured filename
    """
    # Remove any path components
    filename = Path(filename).name
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove any characters that aren't alphanumeric, dash, underscore, or dot
    filename = re.sub(r'[^\w\-.]', '', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1)
        filename = name[:250] + '.' + ext
    
    return filename


def validate_file_size(size: int) -> bool:
    """
    Validate if file size is within allowed limit
    
    Args:
        size: File size in bytes
        
    Returns:
        True if size is allowed, False otherwise
    """
    return 0 < size <= FileUploadDefaults.MAX_FILE_SIZE

