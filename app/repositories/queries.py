"""
SQL Query Constants for File Repository
All SQL queries are defined here to avoid magic strings
"""

# Note: FileStatus has been moved to app/constants.py


class FileQueries:
    """SQL queries for file operations"""
    
    # CREATE
    INSERT_FILE = """
        INSERT INTO files 
        (id, filename, original_filename, file_size, lines_count, checksum, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    # READ
    SELECT_FILE_BY_ID = """
        SELECT id, filename, original_filename, file_size, lines_count,
               uploaded_at, checksum, status
        FROM files
        WHERE id = ? AND status = ?
    """
    
    SELECT_ALL_FILES = """
        SELECT id, filename, original_filename, file_size, lines_count,
               uploaded_at, checksum, status
        FROM files
        WHERE status = ?
        ORDER BY uploaded_at DESC
        LIMIT ? OFFSET ?
    """
    
    SELECT_FILE_EXISTS = """
        SELECT 1 
        FROM files 
        WHERE id = ? AND status = ?
    """
    
    SELECT_LINES_COUNT = """
        SELECT lines_count 
        FROM files 
        WHERE id = ? AND status = ?
    """
    
    SELECT_FILES_BY_IDS = """
        SELECT id, filename, original_filename, file_size, lines_count,
               uploaded_at, checksum, status
        FROM files
        WHERE id IN ({}) AND status = ?
    """
    
    # UPDATE
    UPDATE_FILE_STATUS = """
        UPDATE files
        SET status = ?
        WHERE id = ? AND status = ?
    """
    
    # DELETE (soft delete via UPDATE)
    SOFT_DELETE_FILE = """
        UPDATE files
        SET status = ?
        WHERE id = ? AND status = ?
    """



