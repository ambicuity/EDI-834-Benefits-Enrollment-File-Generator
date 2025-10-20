"""
EDI 834 Generator for creating ANSI X12 834 benefit enrollment files.

Transforms validated enrollment records into compliant EDI 834 format.
"""

from typing import List, Dict, Any
from datetime import datetime
from .formatter import (
    format_edi_segment,
    format_isa_segment,
    format_gs_segment,
    format_st_segment,
    format_se_segment,
    format_ge_segment,
    format_iea_segment,
    escape_delimiters,
    pad_field
)
from .utils import generate_control_number, format_date, format_time


class EDI834Generator:
    """
    Generator class for creating EDI 834 benefit enrollment files.
    """
    
    def __init__(self, sender_id: str = 'SENDER', receiver_id: str = 'RECEIVER', test_mode: bool = True):
        """
        Initialize the EDI 834 generator.
        
        Args:
            sender_id: Sender identifier (up to 15 chars)
            receiver_id: Receiver identifier (up to 15 chars)
            test_mode: Whether to generate test or production file
        """
        self.sender_id = sender_id[:15]
        self.receiver_id = receiver_id[:15]
        self.test_indicator = 'T' if test_mode else 'P'
        self.control_number = generate_control_number(length=9)
        self.transaction_count = 0
    
    def generate(self, records: List[Dict[str, Any]]) -> str:
        """
        Generate EDI 834 file from enrollment records.
        
        Args:
            records: List of validated enrollment records
            
        Returns:
            Complete EDI 834 file content
        """
        segments = []
        
        # Generate header segments
        segments.extend(self._generate_header())
        
        # Generate enrollment data
        segments.extend(self._generate_transaction_set(records))
        
        # Generate trailer segments
        segments.extend(self._generate_trailer())
        
        return ''.join(segments)
    
    def _generate_header(self) -> List[str]:
        """Generate ISA and GS header segments."""
        segments = []
        
        # Current date and time
        current_date = datetime.now()
        isa_date = current_date.strftime('%y%m%d')  # YYMMDD for ISA
        isa_time = current_date.strftime('%H%M')    # HHMM for ISA
        gs_date = current_date.strftime('%Y%m%d')   # YYYYMMDD for GS
        gs_time = current_date.strftime('%H%M')     # HHMM for GS
        
        # ISA - Interchange Control Header
        segments.append(format_isa_segment(
            self.sender_id,
            self.receiver_id,
            isa_date,
            isa_time,
            self.control_number,
            self.test_indicator
        ))
        
        # GS - Functional Group Header
        segments.append(format_gs_segment(
            self.sender_id,
            self.receiver_id,
            gs_date,
            gs_time,
            self.control_number
        ))
        
        return segments
    
    def _generate_transaction_set(self, records: List[Dict[str, Any]]) -> List[str]:
        """Generate ST, BGN, and enrollment loop segments."""
        segments = []
        segment_count = 0
        
        # ST - Transaction Set Header
        transaction_control = generate_control_number(length=4)
        segments.append(format_st_segment(transaction_control))
        segment_count += 1
        
        # BGN - Beginning Segment
        current_date = datetime.now()
        bgn_date = current_date.strftime('%Y%m%d')
        bgn_time = current_date.strftime('%H%M%S')
        
        bgn_elements = [
            '00',                       # Transaction Set Purpose Code (Original)
            transaction_control,        # Transaction Set Reference Number
            bgn_date,                   # Date
            bgn_time,                   # Time
            'ET',                       # Time Zone
            '',                         # Reference ID
            '',                         # Transaction Type
            '4',                        # Action Code (Change)
        ]
        segments.append(format_edi_segment('BGN', bgn_elements))
        segment_count += 1
        
        # REF - Reference Identification (optional, for transaction reference)
        ref_elements = ['38', transaction_control]  # 38 = Employer's ID
        segments.append(format_edi_segment('REF', ref_elements))
        segment_count += 1
        
        # DTP - File Effective Date
        dtp_elements = ['007', 'D8', bgn_date]  # 007 = Effective Date
        segments.append(format_edi_segment('DTP', dtp_elements))
        segment_count += 1
        
        # Generate sponsor (1000A) loop
        sponsor_segments, sponsor_count = self._generate_sponsor_loop()
        segments.extend(sponsor_segments)
        segment_count += sponsor_count
        
        # Generate member (2000) loops for each enrollment record
        for record in records:
            member_segments, member_count = self._generate_member_loop(record)
            segments.extend(member_segments)
            segment_count += member_count
        
        # SE - Transaction Set Trailer
        segment_count += 1  # Count the SE segment itself
        segments.append(format_se_segment(segment_count, transaction_control))
        
        self.transaction_count = 1
        
        return segments
    
    def _generate_sponsor_loop(self) -> tuple:
        """Generate 1000A sponsor loop segments."""
        segments = []
        count = 0
        
        # NM1 - Sponsor Name (1000A)
        nm1_elements = [
            'P5',                       # Entity Identifier Code (Plan Sponsor)
            '2',                        # Entity Type (Non-Person)
            self.sender_id,             # Organization Name
            '',                         # First Name
            '',                         # Middle Name
            '',                         # Prefix
            '',                         # Suffix
            'FI',                       # ID Code Qualifier (Federal Taxpayer ID)
            self.sender_id,             # Identification Code
        ]
        segments.append(format_edi_segment('NM1', nm1_elements))
        count += 1
        
        return segments, count
    
    def _generate_member_loop(self, record: Dict[str, Any]) -> tuple:
        """Generate 2000 member loop segments."""
        segments = []
        count = 0
        
        # INS - Insured Benefit
        ins_elements = [
            'Y',                                    # Yes/No (Y = Info in this TS applies to person)
            record.get('relationship_code', '18'),  # Relationship Code
            '021',                                  # Maintenance Type Code (021 = Change)
            '01',                                   # Maintenance Reason (01 = Change in ID Card)
            'A',                                    # Benefit Status (A = Active)
            '',                                     # Medicare Plan Code
            '',                                     # COBRA Qualifier
            'FT',                                   # Employment Status (FT = Full Time)
        ]
        segments.append(format_edi_segment('INS', ins_elements))
        count += 1
        
        # REF - Subscriber ID
        if record.get('subscriber_id') or record.get('employee_id'):
            ref_elements = [
                '0F',                               # Reference ID Qualifier (Subscriber Number)
                escape_delimiters(record.get('subscriber_id') or record.get('employee_id')),
            ]
            segments.append(format_edi_segment('REF', ref_elements))
            count += 1
        
        # REF - Member Policy Number (optional)
        if record.get('employee_id'):
            ref_elements = [
                '1L',                               # Group/Policy Number
                escape_delimiters(record.get('employee_id')),
            ]
            segments.append(format_edi_segment('REF', ref_elements))
            count += 1
        
        # DTP - Member Level Dates
        if record.get('coverage_start'):
            dtp_elements = [
                '348',                              # Benefit Begin Date
                'D8',                               # Date Format
                record['coverage_start'],
            ]
            segments.append(format_edi_segment('DTP', dtp_elements))
            count += 1
        
        if record.get('coverage_end'):
            dtp_elements = [
                '349',                              # Benefit End Date
                'D8',
                record['coverage_end'],
            ]
            segments.append(format_edi_segment('DTP', dtp_elements))
            count += 1
        
        # NM1 - Member Name (2100A)
        nm1_elements = [
            'IL',                                   # Entity Identifier (Insured/Subscriber)
            '1',                                    # Entity Type (Person)
            escape_delimiters(record.get('last_name', '')),
            escape_delimiters(record.get('first_name', '')),
            escape_delimiters(record.get('middle_name', '')),
            '',                                     # Prefix
            '',                                     # Suffix
            '34',                                   # ID Code Qualifier (SSN)
            record.get('ssn', ''),
        ]
        segments.append(format_edi_segment('NM1', nm1_elements))
        count += 1
        
        # N3 - Member Address
        if record.get('address1'):
            n3_elements = [
                escape_delimiters(record['address1']),
                escape_delimiters(record.get('address2', '')),
            ]
            segments.append(format_edi_segment('N3', n3_elements))
            count += 1
        
        # N4 - Member City/State/ZIP
        if record.get('city') or record.get('state') or record.get('zip'):
            n4_elements = [
                escape_delimiters(record.get('city', '')),
                record.get('state', '').upper(),
                record.get('zip', '').split('-')[0] if record.get('zip') else '',
            ]
            segments.append(format_edi_segment('N4', n4_elements))
            count += 1
        
        # DMG - Demographic Information
        if record.get('dob') or record.get('gender'):
            dmg_elements = [
                'D8',                               # Date Format
                record.get('dob', ''),
                record.get('gender', 'U'),
            ]
            segments.append(format_edi_segment('DMG', dmg_elements))
            count += 1
        
        # HD - Health Coverage (2300)
        if record.get('plan_code'):
            hd_elements = [
                '021',                              # Maintenance Type Code
                '',                                 # Maintenance Reason
                'HLT',                              # Insurance Line Code (Health)
                escape_delimiters(record.get('plan_code', '')),
                'EMP',                              # Coverage Level (Employee Only)
            ]
            segments.append(format_edi_segment('HD', hd_elements))
            count += 1
            
            # DTP - Health Coverage Dates
            if record.get('coverage_start'):
                dtp_elements = [
                    '348',                          # Coverage Begin
                    'D8',
                    record['coverage_start'],
                ]
                segments.append(format_edi_segment('DTP', dtp_elements))
                count += 1
        
        return segments, count
    
    def _generate_trailer(self) -> List[str]:
        """Generate GE and IEA trailer segments."""
        segments = []
        
        # GE - Functional Group Trailer
        segments.append(format_ge_segment(self.transaction_count, self.control_number))
        
        # IEA - Interchange Control Trailer
        segments.append(format_iea_segment(1, self.control_number))
        
        return segments


def generate_834(records: List[Dict[str, Any]], sender_id: str = 'SENDER', 
                 receiver_id: str = 'RECEIVER', test_mode: bool = True) -> str:
    """
    Generate EDI 834 file from enrollment records.
    
    Args:
        records: List of validated enrollment records
        sender_id: Sender identifier
        receiver_id: Receiver identifier
        test_mode: Whether to generate test or production file
        
    Returns:
        Complete EDI 834 file content
    """
    generator = EDI834Generator(sender_id, receiver_id, test_mode)
    return generator.generate(records)
