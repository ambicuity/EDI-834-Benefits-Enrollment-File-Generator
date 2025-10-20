# EDI 834 Benefits Enrollment File Generator - Overview

## Introduction

The EDI 834 Benefits Enrollment File Generator is a Python-based tool that converts employee benefits enrollment data from CSV format into compliant ANSI X12 834 EDI files. This tool is designed to simplify the process of generating standardized benefit enrollment files for transmission to insurance carriers and benefits providers.

## What is EDI 834?

EDI 834 (Benefit Enrollment and Maintenance) is an ANSI X12 transaction set used to transmit employee benefit enrollment information between employers, payroll providers, and insurance carriers. It's the standard format for communicating:

- New employee enrollments
- Benefit plan changes
- Dependent additions/removals
- Coverage terminations
- Personal information updates

## Key Features

### 1. **Easy CSV Input**
- Simple CSV format for enrollment data
- Flexible column naming (supports common variations)
- Automatic data normalization

### 2. **Comprehensive Validation**
- Required field validation
- SSN format checking
- Date format validation
- Plan code verification
- Field length limits
- Business rule enforcement

### 3. **Compliant EDI Generation**
- ANSI X12 005010X220A1 standard
- Proper segment hierarchy (ISA → GS → ST → loops → SE → GE → IEA)
- Automatic control number generation
- Test and production modes

### 4. **User-Friendly CLI**
- Simple command-line interface
- Colored console output (with rich library)
- Progress indicators
- Detailed error reporting

### 5. **Flexible Output**
- Standard EDI format
- Pretty-printed format for readability
- JSON conversion for debugging
- Validation reports (text, JSON, CSV)

## Architecture

### Components

```
┌─────────────┐
│   CSV File  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parser    │  ← Reads and normalizes CSV data
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Validator  │  ← Validates against business rules
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generator  │  ← Creates EDI 834 segments
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Formatter  │  ← Formats and validates output
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  EDI File   │
└─────────────┘
```

### Data Flow

1. **Input**: Employee enrollment data in CSV format
2. **Parsing**: CSV data is read and normalized into Python dictionaries
3. **Validation**: Records are validated against configurable business rules
4. **Generation**: Valid records are transformed into EDI 834 segments
5. **Formatting**: Segments are formatted with proper delimiters and structure
6. **Output**: Complete EDI 834 file ready for transmission

## Use Cases

### HR Departments
- Upload monthly enrollment changes to insurance carriers
- Onboard new employees with benefit selections
- Process open enrollment data

### Benefits Administrators
- Transmit enrollment data to multiple carriers
- Maintain benefit eligibility records
- Handle life event changes

### Payroll Providers
- Sync employee benefit elections with carriers
- Automate enrollment file generation
- Reduce manual data entry errors

### System Integrators
- Build automated enrollment workflows
- Integrate with HRIS systems
- Create carrier-specific file feeds

## Technical Requirements

- **Python**: 3.8 or higher
- **Dependencies**:
  - pyyaml (configuration management)
  - pandas (data processing, optional)
  - rich (console formatting)
  - pytest (testing)

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator.git
cd EDI-834-Benefits-Enrollment-File-Generator

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Quick Start

```bash
# Generate EDI file from CSV
python -m edi834.cli --input examples/sample_input.csv --output output/benefits_834.edi

# Validate data without generating
python -m edi834.cli --input data.csv --validate-only

# Generate with validation report
python -m edi834.cli --input data.csv --output out.edi --validation-report report.txt
```

## Configuration

The tool uses YAML configuration files for:

1. **Validation Rules** (`edi834/config/validation_rules.yaml`)
   - Required fields
   - Valid plan codes
   - Pattern matching rules
   - Field length limits

2. **Segment Mapping** (`edi834/config/segment_map.yaml`)
   - EDI segment definitions
   - Element mappings
   - Segment structure

## Support

For issues, questions, or contributions:
- GitHub Issues: [Report a bug or request a feature]
- Documentation: See the `/docs` directory for detailed guides
- Examples: Check `/examples` for sample input/output files

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Ritesh Rana**
- Project: EDI 834 Benefits Enrollment File Generator
- Repository: https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator

## Next Steps

- Read [Input Specification](input_specification.md) to understand CSV format requirements
- Review [EDI Structure](edi_structure.md) to learn about EDI 834 format
- Check [Validation Rules](validation_rules.md) for data quality requirements
- Consult [Troubleshooting](troubleshooting.md) if you encounter issues
