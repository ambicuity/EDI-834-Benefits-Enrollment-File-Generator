"""
EDI 834 Benefits Enrollment File Generator

A Python-based ETL and EDI 834 generator that converts employee benefits 
enrollment data (CSV) into a compliant ANSI X12 834 file.

Author: Ritesh Rana
"""

__version__ = "1.0.0"
__author__ = "Ritesh Rana"

from .parser import parse_csv
from .validator import validate_records
from .generator import generate_834
from .formatter import format_edi_segment

__all__ = [
    "parse_csv",
    "validate_records",
    "generate_834",
    "format_edi_segment",
]
