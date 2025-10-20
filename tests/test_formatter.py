"""
Tests for the formatter module.
"""

import pytest
from edi834.formatter import (
    format_edi_segment,
    pad_field,
    format_isa_segment,
    format_gs_segment,
    format_st_segment,
    format_se_segment,
    format_ge_segment,
    format_iea_segment,
    pretty_print_edi,
    edi_to_json,
    validate_edi_structure,
    escape_delimiters
)


def test_format_edi_segment():
    """Test basic EDI segment formatting."""
    segment = format_edi_segment('ST', ['834', '0001'])
    
    assert segment == 'ST*834*0001~'


def test_format_edi_segment_with_empty_elements():
    """Test EDI segment formatting with empty elements."""
    segment = format_edi_segment('NM1', ['IL', '1', 'DOE', 'JOHN', ''])
    
    assert segment == 'NM1*IL*1*DOE*JOHN*~'


def test_pad_field_left():
    """Test left-aligned padding."""
    result = pad_field('TEST', 10, ' ', 'left')
    
    assert result == 'TEST      '
    assert len(result) == 10


def test_pad_field_right():
    """Test right-aligned padding."""
    result = pad_field('123', 9, '0', 'right')
    
    assert result == '000000123'
    assert len(result) == 9


def test_pad_field_truncate():
    """Test field truncation when too long."""
    result = pad_field('VERYLONGTEXT', 5, ' ', 'left')
    
    assert result == 'VERYL'
    assert len(result) == 5


def test_format_isa_segment():
    """Test ISA segment formatting."""
    isa = format_isa_segment('SENDER', 'RECEIVER', '241020', '1200', '000000001', 'T')
    
    assert isa.startswith('ISA*')
    assert isa.endswith('~')
    assert 'SENDER' in isa
    assert 'RECEIVER' in isa
    assert '241020' in isa
    assert '1200' in isa
    assert '*T*' in isa  # Test indicator


def test_format_gs_segment():
    """Test GS segment formatting."""
    gs = format_gs_segment('SENDER', 'RECEIVER', '20241020', '1200', '1')
    
    assert gs.startswith('GS*')
    assert gs.endswith('~')
    assert 'BE*' in gs  # Functional identifier
    assert 'SENDER' in gs
    assert 'RECEIVER' in gs
    assert '005010X220A1' in gs  # Version


def test_format_st_segment():
    """Test ST segment formatting."""
    st = format_st_segment('0001')
    
    assert st.startswith('ST*')
    assert st.endswith('~')
    assert 'ST*834*0001*' in st


def test_format_se_segment():
    """Test SE segment formatting."""
    se = format_se_segment(15, '0001')
    
    assert se == 'SE*15*0001~'


def test_format_ge_segment():
    """Test GE segment formatting."""
    ge = format_ge_segment(1, '1')
    
    assert ge == 'GE*1*1~'


def test_format_iea_segment():
    """Test IEA segment formatting."""
    iea = format_iea_segment(1, '1')
    
    assert iea.startswith('IEA*')
    assert iea.endswith('~')


def test_pretty_print_edi():
    """Test pretty printing of EDI content."""
    edi_content = 'ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *241020*1200*^*00501*000000001*0*T*:~GS*BE*SENDER*RECEIVER*20241020*1200*1*X*005010X220A1~ST*834*0001*005010X220A1~'
    
    pretty = pretty_print_edi(edi_content, segments_per_line=1)
    
    # Should have line breaks
    assert '\n' in pretty
    
    # Each segment should end with ~
    lines = pretty.split('\n')
    for line in lines:
        if line.strip():
            assert '~' in line


def test_edi_to_json():
    """Test EDI to JSON conversion."""
    edi_content = 'ISA*00*          *ZZ*SENDER~GS*BE*SENDER*RECEIVER~'
    
    json_output = edi_to_json(edi_content)
    
    assert 'ISA' in json_output
    assert 'GS' in json_output
    
    import json
    data = json.loads(json_output)
    
    assert len(data) == 2
    assert data[0]['segment'] == 'ISA'
    assert data[1]['segment'] == 'GS'


def test_escape_delimiters():
    """Test delimiter escaping."""
    text = "Test*with~delimiters:here"
    
    escaped = escape_delimiters(text)
    
    # Delimiters should be replaced with spaces
    assert '*' not in escaped
    assert '~' not in escaped
    assert ':' not in escaped


def test_escape_delimiters_none_value():
    """Test escaping with None value."""
    result = escape_delimiters(None)
    
    assert result == ''


def test_validate_edi_structure_valid():
    """Test EDI structure validation with valid content."""
    edi_content = 'ISA*00*          *ZZ*SENDER~GS*BE*SENDER*RECEIVER~ST*834*0001~BGN*00*001~SE*4*0001~GE*1*1~IEA*1*000000001~'
    
    result = validate_edi_structure(edi_content)
    
    assert result['valid'] is True
    assert len(result['errors']) == 0
    assert result['segment_count'] > 0


def test_validate_edi_structure_missing_isa():
    """Test EDI structure validation with missing ISA."""
    edi_content = 'GS*BE*SENDER*RECEIVER~ST*834*0001~SE*3*0001~GE*1*1~IEA*1*000000001~'
    
    result = validate_edi_structure(edi_content)
    
    assert result['valid'] is False
    assert any('ISA' in error for error in result['errors'])


def test_validate_edi_structure_missing_iea():
    """Test EDI structure validation with missing IEA."""
    edi_content = 'ISA*00*          *ZZ*SENDER~GS*BE*SENDER*RECEIVER~ST*834*0001~SE*3*0001~GE*1*1~'
    
    result = validate_edi_structure(edi_content)
    
    assert result['valid'] is False
    assert any('IEA' in error for error in result['errors'])


def test_validate_edi_structure_missing_required_segments():
    """Test EDI structure validation with missing required segments."""
    edi_content = 'ISA*00*          *ZZ*SENDER~IEA*1*000000001~'
    
    result = validate_edi_structure(edi_content)
    
    assert result['valid'] is False
    # Should have errors for missing GS, ST, SE, GE
    assert len(result['errors']) > 0


def test_format_edi_segment_custom_delimiters():
    """Test EDI segment formatting with custom delimiters."""
    segment = format_edi_segment('ST', ['834', '0001'], element_separator='|', segment_terminator='\n')
    
    assert segment == 'ST|834|0001\n'


def test_pad_field_zero_length():
    """Test padding with zero or negative length."""
    result = pad_field('TEST', 0, ' ', 'left')
    
    # Should truncate to 0
    assert result == ''
