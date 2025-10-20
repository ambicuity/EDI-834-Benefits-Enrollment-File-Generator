"""
Tests for the validator module.
"""

import pytest
from edi834.validator import (
    validate_record,
    validate_records,
    load_validation_rules,
    generate_validation_report
)


def test_validate_record_valid():
    """Test validation of a valid record."""
    record = {
        'employee_id': '12345',
        'ssn': '111223333',
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '19850115',
        'plan_code': 'MED001',
        'coverage_start': '20240101',
    }
    
    rules = load_validation_rules()
    errors = validate_record(record, rules)
    
    assert len(errors) == 0


def test_validate_record_missing_required_field():
    """Test validation with missing required field."""
    record = {
        'employee_id': '12345',
        'first_name': 'John',
        'last_name': 'Doe',
        # Missing ssn
    }
    
    rules = load_validation_rules()
    errors = validate_record(record, rules)
    
    assert len(errors) > 0
    assert any('ssn' in error.lower() for error in errors)


def test_validate_record_invalid_ssn():
    """Test validation with invalid SSN format."""
    record = {
        'employee_id': '12345',
        'ssn': '12345',  # Too short
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '19850115',
        'plan_code': 'MED001',
        'coverage_start': '20240101',
    }
    
    rules = load_validation_rules()
    errors = validate_record(record, rules)
    
    assert len(errors) > 0
    assert any('ssn' in error.lower() for error in errors)


def test_validate_record_invalid_date():
    """Test validation with invalid date format."""
    record = {
        'employee_id': '12345',
        'ssn': '111223333',
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '01/15/1985',  # Wrong format
        'plan_code': 'MED001',
        'coverage_start': '20240101',
    }
    
    rules = load_validation_rules()
    errors = validate_record(record, rules)
    
    assert len(errors) > 0
    assert any('date' in error.lower() for error in errors)


def test_validate_record_invalid_plan_code():
    """Test validation with invalid plan code."""
    record = {
        'employee_id': '12345',
        'ssn': '111223333',
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '19850115',
        'plan_code': 'INVALID999',
        'coverage_start': '20240101',
    }
    
    rules = load_validation_rules()
    errors = validate_record(record, rules)
    
    assert len(errors) > 0
    assert any('plan code' in error.lower() for error in errors)


def test_validate_records_multiple():
    """Test validation of multiple records."""
    records = [
        {
            'employee_id': '12345',
            'ssn': '111223333',
            'first_name': 'John',
            'last_name': 'Doe',
            'dob': '19850115',
            'plan_code': 'MED001',
            'coverage_start': '20240101',
        },
        {
            'employee_id': '23456',
            'ssn': '222334444',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'dob': '19900322',
            'plan_code': 'MED001',
            'coverage_start': '20240101',
        },
    ]
    
    results = validate_records(records)
    
    assert results['total_records'] == 2
    assert results['valid_records'] == 2
    assert results['invalid_records'] == 0
    assert results['valid'] is True


def test_validate_records_with_errors():
    """Test validation with some invalid records."""
    records = [
        {
            'employee_id': '12345',
            'ssn': '111223333',
            'first_name': 'John',
            'last_name': 'Doe',
            'dob': '19850115',
            'plan_code': 'MED001',
            'coverage_start': '20240101',
        },
        {
            'employee_id': '23456',
            # Missing required fields
            'first_name': 'Jane',
        },
    ]
    
    results = validate_records(records)
    
    assert results['total_records'] == 2
    assert results['valid_records'] == 1
    assert results['invalid_records'] == 1
    assert results['valid'] is False


def test_validate_coverage_dates():
    """Test validation of coverage date logic."""
    record = {
        'employee_id': '12345',
        'ssn': '111223333',
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '19850115',
        'plan_code': 'MED001',
        'coverage_start': '20240201',
        'coverage_end': '20240101',  # End before start
    }
    
    rules = load_validation_rules()
    errors = validate_record(record, rules)
    
    assert len(errors) > 0
    assert any('coverage' in error.lower() for error in errors)


def test_validate_zip_code():
    """Test ZIP code validation."""
    rules = load_validation_rules()
    
    # Valid ZIP codes
    valid_record = {
        'employee_id': '12345',
        'ssn': '111223333',
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '19850115',
        'plan_code': 'MED001',
        'coverage_start': '20240101',
        'zip': '12345',
    }
    errors = validate_record(valid_record, rules)
    zip_errors = [e for e in errors if 'zip' in e.lower()]
    assert len(zip_errors) == 0
    
    # Invalid ZIP code
    invalid_record = valid_record.copy()
    invalid_record['zip'] = '123'
    errors = validate_record(invalid_record, rules)
    zip_errors = [e for e in errors if 'zip' in e.lower()]
    assert len(zip_errors) > 0


def test_generate_validation_report_text():
    """Test text format validation report generation."""
    results = {
        'total_records': 2,
        'valid_records': 1,
        'invalid_records': 1,
        'errors': [
            {
                'record': 2,
                'row_number': 2,
                'employee_id': '23456',
                'errors': ['Missing required field: ssn']
            }
        ]
    }
    
    report = generate_validation_report(results, 'text')
    
    assert 'VALIDATION REPORT' in report
    assert 'Total Records: 2' in report
    assert 'Valid Records: 1' in report


def test_generate_validation_report_json():
    """Test JSON format validation report generation."""
    results = {
        'total_records': 2,
        'valid_records': 2,
        'invalid_records': 0,
        'errors': []
    }
    
    report = generate_validation_report(results, 'json')
    
    import json
    data = json.loads(report)
    assert data['total_records'] == 2
    assert data['valid_records'] == 2
