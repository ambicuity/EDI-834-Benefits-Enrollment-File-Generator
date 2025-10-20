"""
EDI Formatter for generating properly formatted EDI segments.

Handles formatting, padding, and delimiter management for EDI 834 files.
"""

from typing import List, Dict, Any
import json


def format_edi_segment(segment_tag: str, elements: List[str], element_separator: str = '*', segment_terminator: str = '~') -> str:
    """
    Format an EDI segment with proper delimiters.
    
    Args:
        segment_tag: EDI segment identifier (e.g., 'ISA', 'GS', 'ST')
        elements: List of segment elements
        element_separator: Character separating elements (default: *)
        segment_terminator: Character terminating segment (default: ~)
        
    Returns:
        Formatted EDI segment string
    """
    # Filter out None values and convert to strings
    formatted_elements = [str(elem) if elem is not None else '' for elem in elements]
    
    # Join elements with separator
    segment = segment_tag + element_separator + element_separator.join(formatted_elements)
    
    # Add segment terminator
    return segment + segment_terminator


def pad_field(value: str, length: int, pad_char: str = ' ', align: str = 'left') -> str:
    """
    Pad a field to a specific length.
    
    Args:
        value: Value to pad
        length: Target length
        pad_char: Character to use for padding
        align: Alignment ('left' or 'right')
        
    Returns:
        Padded string
    """
    value = str(value) if value else ''
    
    if len(value) >= length:
        return value[:length]
    
    padding = pad_char * (length - len(value))
    
    if align == 'right':
        return padding + value
    else:
        return value + padding


def format_isa_segment(sender_id: str, receiver_id: str, date: str, time: str, 
                       control_number: str, test_indicator: str = 'T') -> str:
    """
    Format ISA (Interchange Control Header) segment.
    
    Args:
        sender_id: Sender identifier
        receiver_id: Receiver identifier
        date: Date in YYMMDD format
        time: Time in HHMM format
        control_number: Interchange control number
        test_indicator: T for test, P for production
        
    Returns:
        Formatted ISA segment
    """
    elements = [
        '00',                           # I01: Authorization Info Qualifier
        pad_field('', 10),              # I02: Authorization Information
        '00',                           # I03: Security Info Qualifier
        pad_field('', 10),              # I04: Security Information
        'ZZ',                           # I05: Interchange ID Qualifier
        pad_field(sender_id, 15),       # I06: Interchange Sender ID
        'ZZ',                           # I07: Interchange ID Qualifier
        pad_field(receiver_id, 15),     # I08: Interchange Receiver ID
        date,                           # I09: Interchange Date
        time,                           # I10: Interchange Time
        '^',                            # I11: Repetition Separator
        '00501',                        # I12: Interchange Control Version
        pad_field(control_number, 9, '0', 'right'),  # I13: Control Number
        '0',                            # I14: Acknowledgment Requested
        test_indicator,                 # I15: Usage Indicator
        ':',                            # I16: Component Element Separator
    ]
    
    return format_edi_segment('ISA', elements)


def format_gs_segment(sender_code: str, receiver_code: str, date: str, time: str, control_number: str) -> str:
    """
    Format GS (Functional Group Header) segment.
    
    Args:
        sender_code: Application sender's code
        receiver_code: Application receiver's code
        date: Date in YYYYMMDD format
        time: Time in HHMM or HHMMSS format
        control_number: Group control number
        
    Returns:
        Formatted GS segment
    """
    elements = [
        'BE',                           # GS01: Functional Identifier Code
        sender_code,                    # GS02: Application Sender's Code
        receiver_code,                  # GS03: Application Receiver's Code
        date,                           # GS04: Date
        time,                           # GS05: Time
        control_number,                 # GS06: Group Control Number
        'X',                            # GS07: Responsible Agency Code
        '005010X220A1',                 # GS08: Version/Release/Industry ID
    ]
    
    return format_edi_segment('GS', elements)


def format_st_segment(control_number: str) -> str:
    """
    Format ST (Transaction Set Header) segment.
    
    Args:
        control_number: Transaction set control number
        
    Returns:
        Formatted ST segment
    """
    elements = [
        '834',                          # ST01: Transaction Set Identifier
        control_number,                 # ST02: Transaction Set Control Number
        '005010X220A1',                 # ST03: Implementation Convention Reference
    ]
    
    return format_edi_segment('ST', elements)


def format_se_segment(segment_count: int, control_number: str) -> str:
    """
    Format SE (Transaction Set Trailer) segment.
    
    Args:
        segment_count: Number of segments in the transaction set
        control_number: Transaction set control number
        
    Returns:
        Formatted SE segment
    """
    elements = [
        str(segment_count),             # SE01: Number of Included Segments
        control_number,                 # SE02: Transaction Set Control Number
    ]
    
    return format_edi_segment('SE', elements)


def format_ge_segment(transaction_count: int, control_number: str) -> str:
    """
    Format GE (Functional Group Trailer) segment.
    
    Args:
        transaction_count: Number of transaction sets
        control_number: Group control number
        
    Returns:
        Formatted GE segment
    """
    elements = [
        str(transaction_count),         # GE01: Number of Transaction Sets
        control_number,                 # GE02: Group Control Number
    ]
    
    return format_edi_segment('GE', elements)


def format_iea_segment(group_count: int, control_number: str) -> str:
    """
    Format IEA (Interchange Control Trailer) segment.
    
    Args:
        group_count: Number of functional groups
        control_number: Interchange control number
        
    Returns:
        Formatted IEA segment
    """
    elements = [
        str(group_count),               # IEA01: Number of Functional Groups
        pad_field(control_number, 9, '0', 'right'),  # IEA02: Interchange Control Number
    ]
    
    return format_edi_segment('IEA', elements)


def pretty_print_edi(edi_content: str, segments_per_line: int = 1) -> str:
    """
    Format EDI content for human readability.
    
    Args:
        edi_content: Raw EDI content
        segments_per_line: Number of segments per line
        
    Returns:
        Formatted EDI string with line breaks
    """
    segments = edi_content.split('~')
    segments = [s for s in segments if s.strip()]  # Remove empty segments
    
    lines = []
    for i in range(0, len(segments), segments_per_line):
        batch = segments[i:i + segments_per_line]
        lines.append('~\n'.join(batch) + '~')
    
    return '\n'.join(lines)


def edi_to_json(edi_content: str) -> str:
    """
    Convert EDI content to JSON format for debugging.
    
    Args:
        edi_content: Raw EDI content
        
    Returns:
        JSON string representation of EDI structure
    """
    segments = edi_content.split('~')
    segments = [s for s in segments if s.strip()]
    
    json_structure = []
    
    for segment in segments:
        if '*' in segment:
            parts = segment.split('*')
            segment_tag = parts[0]
            elements = parts[1:]
            
            json_structure.append({
                'segment': segment_tag,
                'elements': elements
            })
    
    return json.dumps(json_structure, indent=2)


def escape_delimiters(value: str, delimiters: List[str] = None) -> str:
    """
    Escape EDI delimiters in text values.
    
    Args:
        value: Text value to escape
        delimiters: List of delimiter characters to escape
        
    Returns:
        Escaped string
    """
    if value is None:
        return ''
    
    if delimiters is None:
        delimiters = ['*', '~', ':']
    
    value = str(value)
    for delimiter in delimiters:
        # Replace delimiter with space or remove it
        value = value.replace(delimiter, ' ')
    
    return value


def validate_edi_structure(edi_content: str) -> Dict[str, Any]:
    """
    Validate basic EDI structure.
    
    Args:
        edi_content: EDI content to validate
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'segment_count': 0,
    }
    
    # Remove newlines that may have been added by pretty print
    edi_content = edi_content.replace('\n', '')
    
    segments = edi_content.split('~')
    segments = [s for s in segments if s.strip()]
    result['segment_count'] = len(segments)
    
    # Check for ISA header
    if not segments or not segments[0].startswith('ISA'):
        result['valid'] = False
        result['errors'].append('Missing ISA header segment')
    
    # Check for IEA trailer
    if not segments or not segments[-1].startswith('IEA'):
        result['valid'] = False
        result['errors'].append('Missing IEA trailer segment')
    
    # Check for required segments
    segment_tags = [s.split('*')[0] for s in segments if '*' in s]
    
    required_segments = ['ISA', 'GS', 'ST', 'SE', 'GE', 'IEA']
    for required in required_segments:
        if required not in segment_tags:
            result['valid'] = False
            result['errors'].append(f'Missing required segment: {required}')
    
    return result
