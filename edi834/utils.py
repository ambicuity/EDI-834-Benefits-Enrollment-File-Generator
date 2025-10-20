"""
Utility functions for the EDI 834 generator.
"""

from datetime import datetime
import re
from typing import Any, Dict


def clean_string(value: str) -> str:
    """
    Clean and trim whitespace from string values.
    
    Args:
        value: String to clean
        
    Returns:
        Cleaned string with trimmed whitespace
    """
    if value is None:
        return ""
    return str(value).strip()


def format_date(date_str: str, input_format: str = "%m/%d/%Y", output_format: str = "%Y%m%d") -> str:
    """
    Convert date from one format to another.
    
    Args:
        date_str: Date string to convert
        input_format: Format of input date (default: MM/DD/YYYY)
        output_format: Format of output date (default: YYYYMMDD)
        
    Returns:
        Formatted date string
    """
    if not date_str:
        return ""
    
    try:
        # Try to parse with the provided format
        date_obj = datetime.strptime(date_str.strip(), input_format)
        return date_obj.strftime(output_format)
    except ValueError:
        # If already in YYYYMMDD format, validate and return
        if re.match(r'^\d{8}$', date_str.strip()):
            return date_str.strip()
        return ""


def format_time(time_str: str = None) -> str:
    """
    Format time in HHMM format.
    
    Args:
        time_str: Optional time string
        
    Returns:
        Formatted time string in HHMM format
    """
    if time_str:
        return time_str.strip()
    return datetime.now().strftime("%H%M")


def generate_control_number(prefix: str = "", length: int = 9) -> str:
    """
    Generate a control number for EDI segments.
    
    Args:
        prefix: Optional prefix for the control number
        length: Length of the numeric portion
        
    Returns:
        Control number string
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # Take last 'length' digits
    number = timestamp[-length:] if len(timestamp) >= length else timestamp.zfill(length)
    return f"{prefix}{number}" if prefix else number


def pad_field(value: str, length: int, pad_char: str = " ", left: bool = False) -> str:
    """
    Pad a field to a specific length.
    
    Args:
        value: Value to pad
        length: Target length
        pad_char: Character to use for padding
        left: Whether to pad on the left (True) or right (False)
        
    Returns:
        Padded string
    """
    value = str(value)
    if len(value) >= length:
        return value[:length]
    
    padding = pad_char * (length - len(value))
    return padding + value if left else value + padding


def escape_delimiters(value: str, delimiters: list = None) -> str:
    """
    Escape EDI delimiters in text values.
    
    Args:
        value: Text value to escape
        delimiters: List of delimiter characters to escape
        
    Returns:
        Escaped string
    """
    if delimiters is None:
        delimiters = ['*', '~', ':']
    
    for delimiter in delimiters:
        value = value.replace(delimiter, f"\\{delimiter}")
    
    return value


def validate_ssn_format(ssn: str) -> bool:
    """
    Validate SSN format (9 digits).
    
    Args:
        ssn: SSN string to validate
        
    Returns:
        True if valid, False otherwise
    """
    return bool(re.match(r'^\d{9}$', ssn.replace('-', '').replace(' ', '')))


def validate_date_format(date_str: str) -> bool:
    """
    Validate date format (YYYYMMDD).
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not re.match(r'^\d{8}$', date_str):
        return False
    
    try:
        datetime.strptime(date_str, "%Y%m%d")
        return True
    except ValueError:
        return False


def clean_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean all values in a row dictionary.
    
    Args:
        row: Dictionary with row data
        
    Returns:
        Cleaned row dictionary
    """
    return {key: clean_string(value) for key, value in row.items()}
