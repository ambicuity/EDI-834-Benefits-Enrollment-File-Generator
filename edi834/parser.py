"""
CSV Parser for employee enrollment data.

Reads and normalizes employee enrollment CSV data into structured Python dictionaries.
"""

import csv
from typing import List, Dict, Any
from .utils import clean_row, format_date


def parse_csv(file_path: str, encoding: str = 'utf-8') -> List[Dict[str, Any]]:
    """
    Parse CSV file containing employee enrollment data.
    
    Args:
        file_path: Path to the CSV file
        encoding: File encoding (default: utf-8)
        
    Returns:
        List of dictionaries containing parsed and normalized enrollment records
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        csv.Error: If there's an error parsing the CSV
    """
    records = []
    
    try:
        with open(file_path, newline='', encoding=encoding) as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate that we have headers
            if reader.fieldnames is None:
                raise ValueError("CSV file has no headers")
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because row 1 is headers
                try:
                    cleaned_row = clean_row(row)
                    normalized_row = normalize_record(cleaned_row, row_num)
                    records.append(normalized_row)
                except Exception as e:
                    # Add row number to error for debugging
                    print(f"Warning: Error parsing row {row_num}: {str(e)}")
                    continue
                    
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    except csv.Error as e:
        raise csv.Error(f"Error parsing CSV file: {str(e)}")
    
    return records


def normalize_record(row: Dict[str, Any], row_num: int) -> Dict[str, Any]:
    """
    Normalize a single enrollment record.
    
    Standardizes field names, formats dates, and structures the data
    for EDI generation.
    
    Args:
        row: Raw row data from CSV
        row_num: Row number for error reporting
        
    Returns:
        Normalized record dictionary
    """
    # Map common CSV header variations to standard field names
    field_mappings = {
        'employee_id': ['employee_id', 'employeeid', 'emp_id', 'id'],
        'ssn': ['ssn', 'social_security_number', 'social_security'],
        'first_name': ['first_name', 'firstname', 'fname'],
        'last_name': ['last_name', 'lastname', 'lname'],
        'middle_name': ['middle_name', 'middlename', 'mname'],
        'dob': ['dob', 'date_of_birth', 'birth_date', 'birthdate'],
        'gender': ['gender', 'sex'],
        'address1': ['address1', 'address_line1', 'street'],
        'address2': ['address2', 'address_line2'],
        'city': ['city'],
        'state': ['state'],
        'zip': ['zip', 'zipcode', 'zip_code', 'postal_code'],
        'plan_code': ['plan_code', 'plancode', 'plan'],
        'coverage_start': ['coverage_start', 'coverage_start_date', 'effective_date', 'start_date'],
        'coverage_end': ['coverage_end', 'coverage_end_date', 'termination_date', 'end_date'],
        'relationship': ['relationship', 'relation'],
        'subscriber_id': ['subscriber_id', 'subscriberid', 'member_id'],
    }
    
    normalized = {
        'row_number': row_num,
    }
    
    # Map fields from CSV to normalized names
    for standard_name, variations in field_mappings.items():
        value = None
        for variant in variations:
            if variant in row or variant.upper() in row or variant.lower() in row:
                # Try case-insensitive lookup
                for key in row.keys():
                    if key.lower() == variant.lower():
                        value = row[key]
                        break
                if value:
                    break
        
        normalized[standard_name] = value or ''
    
    # Format dates if present
    date_fields = ['dob', 'coverage_start', 'coverage_end']
    for field in date_fields:
        if normalized.get(field):
            formatted_date = format_date(normalized[field])
            if formatted_date:
                normalized[field] = formatted_date
    
    # Clean SSN - remove dashes and spaces
    if normalized.get('ssn'):
        normalized['ssn'] = normalized['ssn'].replace('-', '').replace(' ', '')
    
    # Standardize gender codes
    if normalized.get('gender'):
        gender = normalized['gender'].upper()
        if gender in ['M', 'MALE']:
            normalized['gender'] = 'M'
        elif gender in ['F', 'FEMALE']:
            normalized['gender'] = 'F'
        else:
            normalized['gender'] = 'U'  # Unknown
    
    # Standardize relationship codes
    if normalized.get('relationship'):
        relationship = normalized['relationship'].upper()
        relationship_map = {
            'EMPLOYEE': '18',
            'SELF': '18',
            'SPOUSE': '01',
            'CHILD': '19',
            'DEPENDENT': '19',
        }
        normalized['relationship_code'] = relationship_map.get(relationship, '18')
    else:
        normalized['relationship_code'] = '18'  # Default to employee
    
    return normalized


def validate_csv_structure(file_path: str) -> Dict[str, Any]:
    """
    Validate CSV file structure without fully parsing it.
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        Dictionary with validation results including headers and row count
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'headers': [],
        'row_count': 0,
    }
    
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            if reader.fieldnames is None:
                result['valid'] = False
                result['errors'].append("CSV file has no headers")
                return result
            
            result['headers'] = list(reader.fieldnames)
            
            # Count rows
            for _ in reader:
                result['row_count'] += 1
            
            if result['row_count'] == 0:
                result['warnings'].append("CSV file contains no data rows")
                
    except FileNotFoundError:
        result['valid'] = False
        result['errors'].append(f"File not found: {file_path}")
    except Exception as e:
        result['valid'] = False
        result['errors'].append(f"Error reading file: {str(e)}")
    
    return result
