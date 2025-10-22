"""
Line analysis utilities
"""

from collections import Counter
from typing import Tuple, Optional


def find_most_frequent_letter(line: str) -> Tuple[Optional[str], int]:
    """
    Find the letter that occurs most often in a line
    
    Args:
        line: The line to analyze
        
    Returns:
        Tuple of (most_frequent_letter, frequency)
        Returns (None, 0) if no letters found
    """
    # Filter only alphabetic characters, case-insensitive
    letters = [char.lower() for char in line if char.isalpha()]
    
    if not letters:
        return None, 0
    
    # Count frequencies
    counter = Counter(letters)
    most_common = counter.most_common(1)[0]
    
    return most_common[0], most_common[1]


def reverse_line(line: str) -> str:
    """
    Reverse a line of text
    
    Args:
        line: The line to reverse
        
    Returns:
        Reversed line
    """
    return line[::-1]


def calculate_line_stats(line: str) -> dict:
    """
    Calculate comprehensive stats for a line
    
    Args:
        line: The line to analyze
        
    Returns:
        Dictionary with stats
    """
    most_freq_letter, freq = find_most_frequent_letter(line)
    
    return {
        'length': len(line),
        'most_frequent_letter': most_freq_letter,
        'letter_frequency': freq,
        'word_count': len(line.split()),
        'char_count': len(line)
    }

