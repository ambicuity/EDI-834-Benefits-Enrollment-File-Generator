"""
Tests for the CSV parser module.
"""

import pytest
import os
import tempfile
from edi834.parser import parse_csv, normalize_record, validate_csv_structure


def test_parse_csv_valid_file():
    """Test parsing a valid CSV file."""
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('employee_id,ssn,first_name,last_name,dob,plan_code,coverage_start\n')
        f.write('12345,111223333,John,Doe,01/15/1985,MED001,01/01/2024\n')
        f.write('23456,222334444,Jane,Smith,03/22/1990,MED001,01/01/2024\n')
        temp_file = f.name
    
    try:
        records = parse_csv(temp_file)
        assert len(records) == 2
        assert records[0]['employee_id'] == '12345'
        assert records[0]['first_name'] == 'John'
        assert records[1]['first_name'] == 'Jane'
    finally:
        os.unlink(temp_file)


def test_parse_csv_nonexistent_file():
    """Test parsing a non-existent file."""
    with pytest.raises(FileNotFoundError):
        parse_csv('nonexistent_file.csv')


def test_normalize_record():
    """Test record normalization."""
    raw_record = {
        'employee_id': '12345',
        'ssn': '111-22-3333',
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '01/15/1985',
        'gender': 'Male',
        'relationship': 'Employee',
    }
    
    normalized = normalize_record(raw_record, 1)
    
    assert normalized['ssn'] == '111223333'  # Dashes removed
    assert normalized['dob'] == '19850115'  # Date formatted
    assert normalized['gender'] == 'M'  # Gender standardized
    assert normalized['relationship_code'] == '18'  # Relationship coded


def test_normalize_record_missing_fields():
    """Test normalization with missing fields."""
    raw_record = {
        'first_name': 'John',
        'last_name': 'Doe',
    }
    
    normalized = normalize_record(raw_record, 1)
    
    # Should have empty strings for missing fields
    assert normalized['ssn'] == ''
    assert normalized['dob'] == ''


def test_validate_csv_structure_valid():
    """Test CSV structure validation with valid file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('employee_id,ssn,first_name\n')
        f.write('12345,111223333,John\n')
        temp_file = f.name
    
    try:
        result = validate_csv_structure(temp_file)
        assert result['valid'] is True
        assert result['row_count'] == 1
        assert len(result['headers']) == 3
    finally:
        os.unlink(temp_file)


def test_validate_csv_structure_empty():
    """Test CSV structure validation with empty file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
        f.write('employee_id,ssn\n')
        temp_file = f.name
    
    try:
        result = validate_csv_structure(temp_file)
        assert result['valid'] is True
        assert result['row_count'] == 0
        assert len(result['warnings']) > 0
    finally:
        os.unlink(temp_file)


def test_date_format_variations():
    """Test various date format inputs."""
    # Test MM/DD/YYYY format
    record1 = {'dob': '01/15/1985'}
    normalized1 = normalize_record(record1, 1)
    assert normalized1['dob'] == '19850115'
    
    # Test YYYYMMDD format (already correct)
    record2 = {'dob': '19850115'}
    normalized2 = normalize_record(record2, 1)
    assert normalized2['dob'] == '19850115'


def test_gender_standardization():
    """Test gender code standardization."""
    test_cases = [
        ('M', 'M'),
        ('Male', 'M'),
        ('F', 'F'),
        ('Female', 'F'),
        ('X', 'U'),
        ('', 'U'),
    ]
    
    for input_gender, expected_output in test_cases:
        record = {'gender': input_gender}
        normalized = normalize_record(record, 1)
        assert normalized['gender'] == expected_output


def test_relationship_code_mapping():
    """Test relationship code mapping."""
    test_cases = [
        ('Employee', '18'),
        ('Self', '18'),
        ('Spouse', '01'),
        ('Child', '19'),
        ('Dependent', '19'),
    ]
    
    for input_rel, expected_code in test_cases:
        record = {'relationship': input_rel}
        normalized = normalize_record(record, 1)
        assert normalized['relationship_code'] == expected_code
