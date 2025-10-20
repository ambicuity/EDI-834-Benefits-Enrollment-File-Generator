"""
Data Validator for enrollment records.

Validates enrollment data against business rules before EDI generation.
"""

import re
import yaml
import os
from typing import List, Dict, Any
from .utils import validate_ssn_format, validate_date_format


def load_validation_rules() -> Dict[str, Any]:
    """
    Load validation rules from YAML configuration file.
    
    Returns:
        Dictionary containing validation rules
    """
    config_path = os.path.join(
        os.path.dirname(__file__),
        'config',
        'validation_rules.yaml'
    )
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Return default rules if config file not found
        return {
            'required_fields': ['employee_id', 'ssn', 'first_name', 'last_name', 'dob', 'plan_code', 'coverage_start'],
            'plan_codes': ['MED001', 'DENT001', 'VISION001'],
            'patterns': {
                'ssn': r'^\d{9}$',
                'date': r'^\d{8}$',
            }
        }


def validate_records(records: List[Dict[str, Any]], rules: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Validate a list of enrollment records.
    
    Args:
        records: List of enrollment records to validate
        rules: Optional validation rules (loads from config if not provided)
        
    Returns:
        Dictionary containing validation results with errors and warnings
    """
    if rules is None:
        rules = load_validation_rules()
    
    results = {
        'valid': True,
        'total_records': len(records),
        'valid_records': 0,
        'invalid_records': 0,
        'errors': [],
        'warnings': [],
    }
    
    for idx, record in enumerate(records):
        record_errors = validate_record(record, rules)
        
        if record_errors:
            results['invalid_records'] += 1
            results['valid'] = False
            results['errors'].append({
                'record': idx + 1,
                'row_number': record.get('row_number', idx + 1),
                'employee_id': record.get('employee_id', 'N/A'),
                'errors': record_errors
            })
        else:
            results['valid_records'] += 1
    
    return results


def validate_record(record: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    """
    Validate a single enrollment record.
    
    Args:
        record: Single enrollment record to validate
        rules: Validation rules
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Check required fields
    required_fields = rules.get('required_fields', [])
    for field in required_fields:
        if not record.get(field):
            errors.append(f"Missing required field: {field}")
    
    # Validate SSN format
    if record.get('ssn'):
        if not validate_ssn_format(record['ssn']):
            errors.append(f"Invalid SSN format: {record['ssn']}")
    
    # Validate date formats
    date_fields = ['dob', 'coverage_start', 'coverage_end']
    for field in date_fields:
        if record.get(field):
            if not validate_date_format(record[field]):
                errors.append(f"Invalid date format for {field}: {record[field]} (expected YYYYMMDD)")
    
    # Validate plan code
    valid_plan_codes = rules.get('plan_codes', [])
    if record.get('plan_code') and valid_plan_codes:
        if record['plan_code'] not in valid_plan_codes:
            errors.append(f"Invalid plan code: {record['plan_code']}")
    
    # Validate field lengths
    max_lengths = rules.get('max_lengths', {})
    for field, max_length in max_lengths.items():
        if record.get(field) and len(str(record[field])) > max_length:
            errors.append(f"Field {field} exceeds maximum length of {max_length}")
    
    # Validate ZIP code format
    if record.get('zip'):
        zip_pattern = rules.get('patterns', {}).get('zip', r'^\d{5}(-\d{4})?$')
        if not re.match(zip_pattern, record['zip']):
            errors.append(f"Invalid ZIP code format: {record['zip']}")
    
    # Validate state code
    if record.get('state'):
        state_pattern = rules.get('patterns', {}).get('state', r'^[A-Z]{2}$')
        if not re.match(state_pattern, record['state'].upper()):
            errors.append(f"Invalid state code: {record['state']} (expected 2-letter state code)")
    
    # Validate gender
    if record.get('gender'):
        valid_genders = rules.get('valid_values', {}).get('gender', ['M', 'F', 'U'])
        if record['gender'] not in valid_genders:
            errors.append(f"Invalid gender code: {record['gender']}")
    
    # Validate relationship code
    if record.get('relationship_code'):
        valid_relationships = rules.get('valid_values', {}).get('relationship_code', ['01', '18', '19', '53'])
        if record['relationship_code'] not in valid_relationships:
            errors.append(f"Invalid relationship code: {record['relationship_code']}")
    
    # Validate coverage dates logic
    if record.get('coverage_start') and record.get('coverage_end'):
        if record['coverage_start'] > record['coverage_end']:
            errors.append(f"Coverage start date ({record['coverage_start']}) is after end date ({record['coverage_end']})")
    
    return errors


def generate_validation_report(validation_results: Dict[str, Any], output_format: str = 'text') -> str:
    """
    Generate a formatted validation report.
    
    Args:
        validation_results: Results from validate_records()
        output_format: Format of the report ('text', 'json', 'csv')
        
    Returns:
        Formatted report string
    """
    if output_format == 'json':
        import json
        return json.dumps(validation_results, indent=2)
    
    elif output_format == 'csv':
        lines = ['Record,Row,Employee ID,Error']
        for error_entry in validation_results.get('errors', []):
            for error in error_entry['errors']:
                lines.append(
                    f"{error_entry['record']},{error_entry['row_number']},"
                    f"{error_entry['employee_id']},\"{error}\""
                )
        return '\n'.join(lines)
    
    else:  # text format
        lines = []
        lines.append("=" * 60)
        lines.append("VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Total Records: {validation_results['total_records']}")
        lines.append(f"Valid Records: {validation_results['valid_records']}")
        lines.append(f"Invalid Records: {validation_results['invalid_records']}")
        lines.append("")
        
        if validation_results['errors']:
            lines.append("ERRORS:")
            lines.append("-" * 60)
            for error_entry in validation_results['errors']:
                lines.append(f"\nRecord #{error_entry['record']} (Row {error_entry['row_number']}, "
                           f"Employee ID: {error_entry['employee_id']}):")
                for error in error_entry['errors']:
                    lines.append(f"  - {error}")
        else:
            lines.append("No errors found. All records are valid!")
        
        lines.append("")
        lines.append("=" * 60)
        
        return '\n'.join(lines)


def save_validation_report(validation_results: Dict[str, Any], output_path: str, output_format: str = 'text'):
    """
    Save validation report to a file.
    
    Args:
        validation_results: Results from validate_records()
        output_path: Path to save the report
        output_format: Format of the report ('text', 'json', 'csv')
    """
    report = generate_validation_report(validation_results, output_format)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
