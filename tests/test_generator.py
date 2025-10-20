"""
Tests for the EDI generator module.
"""

import pytest
from edi834.generator import EDI834Generator, generate_834


def test_generator_initialization():
    """Test generator initialization."""
    generator = EDI834Generator('SENDER123', 'RECEIVER456', test_mode=True)
    
    assert generator.sender_id == 'SENDER123'
    assert generator.receiver_id == 'RECEIVER456'
    assert generator.test_indicator == 'T'


def test_generator_production_mode():
    """Test generator in production mode."""
    generator = EDI834Generator('SENDER123', 'RECEIVER456', test_mode=False)
    
    assert generator.test_indicator == 'P'


def test_generate_834_basic():
    """Test basic EDI 834 generation."""
    records = [
        {
            'employee_id': '12345',
            'ssn': '111223333',
            'first_name': 'John',
            'last_name': 'Doe',
            'dob': '19850115',
            'gender': 'M',
            'plan_code': 'MED001',
            'coverage_start': '20240101',
            'relationship_code': '18',
        }
    ]
    
    edi_content = generate_834(records, 'SENDER', 'RECEIVER', test_mode=True)
    
    # Check that essential segments are present
    assert 'ISA*' in edi_content
    assert 'GS*' in edi_content
    assert 'ST*834*' in edi_content
    assert 'BGN*' in edi_content
    assert 'SE*' in edi_content
    assert 'GE*' in edi_content
    assert 'IEA*' in edi_content
    
    # Check segments end with ~
    assert edi_content.count('~') > 0


def test_generate_834_with_multiple_records():
    """Test EDI 834 generation with multiple records."""
    records = [
        {
            'employee_id': '12345',
            'ssn': '111223333',
            'first_name': 'John',
            'last_name': 'Doe',
            'dob': '19850115',
            'plan_code': 'MED001',
            'coverage_start': '20240101',
            'relationship_code': '18',
        },
        {
            'employee_id': '23456',
            'ssn': '222334444',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'dob': '19900322',
            'plan_code': 'MED001',
            'coverage_start': '20240101',
            'relationship_code': '18',
        },
    ]
    
    edi_content = generate_834(records, 'SENDER', 'RECEIVER')
    
    # Should have multiple member loops
    assert edi_content.count('INS*') == 2
    assert edi_content.count('NM1*IL*') == 2


def test_generate_member_segments():
    """Test member segment generation."""
    generator = EDI834Generator('SENDER', 'RECEIVER')
    
    record = {
        'employee_id': '12345',
        'ssn': '111223333',
        'first_name': 'John',
        'last_name': 'Doe',
        'middle_name': 'M',
        'dob': '19850115',
        'gender': 'M',
        'address1': '123 Main St',
        'city': 'New York',
        'state': 'NY',
        'zip': '10001',
        'plan_code': 'MED001',
        'coverage_start': '20240101',
        'relationship_code': '18',
    }
    
    segments, count = generator._generate_member_loop(record)
    
    assert count > 0
    assert len(segments) > 0
    
    # Check for required segments
    segments_str = ''.join(segments)
    assert 'INS*' in segments_str
    assert 'NM1*IL*' in segments_str
    assert 'N3*' in segments_str
    assert 'N4*' in segments_str
    assert 'DMG*' in segments_str
    assert 'HD*' in segments_str


def test_generate_with_optional_fields():
    """Test generation with optional fields."""
    record = {
        'employee_id': '12345',
        'ssn': '111223333',
        'first_name': 'John',
        'last_name': 'Doe',
        'dob': '19850115',
        'plan_code': 'MED001',
        'coverage_start': '20240101',
        'coverage_end': '20241231',
        'relationship_code': '18',
        'subscriber_id': 'SUB123',
    }
    
    generator = EDI834Generator('SENDER', 'RECEIVER')
    segments, count = generator._generate_member_loop(record)
    
    segments_str = ''.join(segments)
    
    # Should include coverage end date
    assert '349*D8*20241231' in segments_str
    
    # Should include subscriber ID
    assert 'REF*0F*SUB123' in segments_str


def test_isa_segment_format():
    """Test ISA segment formatting."""
    generator = EDI834Generator('SEND', 'RECV')
    header_segments = generator._generate_header()
    
    isa_segment = header_segments[0]
    
    # ISA should start with ISA*
    assert isa_segment.startswith('ISA*')
    
    # ISA should end with ~
    assert isa_segment.endswith('~')
    
    # ISA should have sender and receiver IDs padded to 15 chars
    assert 'SEND           ' in isa_segment  # Padded sender
    assert 'RECV           ' in isa_segment  # Padded receiver


def test_segment_count_in_se():
    """Test that SE segment has correct segment count."""
    records = [
        {
            'employee_id': '12345',
            'ssn': '111223333',
            'first_name': 'John',
            'last_name': 'Doe',
            'dob': '19850115',
            'plan_code': 'MED001',
            'coverage_start': '20240101',
            'relationship_code': '18',
        }
    ]
    
    edi_content = generate_834(records)
    
    # Extract SE segment
    se_segment = [s for s in edi_content.split('~') if s.startswith('SE*')]
    assert len(se_segment) > 0
    
    # SE should have format SE*count*control_number
    se_parts = se_segment[0].split('*')
    assert len(se_parts) >= 3
    segment_count = int(se_parts[1])
    
    # Count should be reasonable (at least 5 for minimal transaction)
    assert segment_count >= 5


def test_control_numbers_present():
    """Test that control numbers are generated."""
    records = [
        {
            'employee_id': '12345',
            'ssn': '111223333',
            'first_name': 'John',
            'last_name': 'Doe',
            'dob': '19850115',
            'plan_code': 'MED001',
            'coverage_start': '20240101',
            'relationship_code': '18',
        }
    ]
    
    generator = EDI834Generator('SENDER', 'RECEIVER')
    
    # Control number should be generated
    assert generator.control_number is not None
    assert len(generator.control_number) > 0


def test_sponsor_loop_generation():
    """Test sponsor loop segment generation."""
    generator = EDI834Generator('ACME_CORP', 'INSURANCE_CO')
    
    sponsor_segments, count = generator._generate_sponsor_loop()
    
    assert count > 0
    assert len(sponsor_segments) > 0
    
    # Should include NM1 segment for sponsor
    sponsor_str = ''.join(sponsor_segments)
    assert 'NM1*P5*' in sponsor_str
    assert 'ACME_CORP' in sponsor_str
