# Input Specification

## CSV File Format

The EDI 834 generator accepts employee enrollment data in CSV (Comma-Separated Values) format. This document describes the required and optional fields, data formats, and examples.

## Required Fields

The following fields **must** be present in your CSV file:

| Field Name | Description | Format | Example |
|------------|-------------|--------|---------|
| `employee_id` | Unique employee identifier | Alphanumeric, max 20 chars | `12345` |
| `ssn` | Social Security Number | 9 digits (no dashes) | `111223333` |
| `first_name` | Employee's first name | Text, max 35 chars | `John` |
| `last_name` | Employee's last name | Text, max 60 chars | `Doe` |
| `dob` | Date of birth | MM/DD/YYYY or YYYYMMDD | `01/15/1985` or `19850115` |
| `plan_code` | Benefit plan identifier | Alphanumeric | `MED001` |
| `coverage_start` | Coverage effective date | MM/DD/YYYY or YYYYMMDD | `01/01/2024` or `20240101` |

## Optional Fields

These fields are optional but recommended for complete enrollment records:

| Field Name | Description | Format | Example |
|------------|-------------|--------|---------|
| `middle_name` | Employee's middle name | Text, max 25 chars | `Michael` |
| `gender` | Gender | M, F, or U (Unknown) | `M` |
| `address1` | Street address line 1 | Text, max 55 chars | `123 Main Street` |
| `address2` | Street address line 2 | Text, max 55 chars | `Apt 4B` |
| `city` | City name | Text, max 30 chars | `New York` |
| `state` | State code | 2-letter state code | `NY` |
| `zip` | ZIP code | 5 or 9 digits | `10001` or `10001-1234` |
| `coverage_end` | Coverage termination date | MM/DD/YYYY or YYYYMMDD | `12/31/2024` |
| `relationship` | Relationship to subscriber | Employee, Spouse, Child, Dependent | `Employee` |
| `subscriber_id` | Subscriber/Member ID | Alphanumeric, max 20 chars | `SUB123456` |

## Column Name Variations

The parser accepts common variations of column names (case-insensitive):

- **employee_id**: `employee_id`, `employeeid`, `emp_id`, `id`
- **ssn**: `ssn`, `social_security_number`, `social_security`
- **first_name**: `first_name`, `firstname`, `fname`
- **last_name**: `last_name`, `lastname`, `lname`
- **dob**: `dob`, `date_of_birth`, `birth_date`, `birthdate`
- **plan_code**: `plan_code`, `plancode`, `plan`
- **coverage_start**: `coverage_start`, `coverage_start_date`, `effective_date`, `start_date`

## Data Format Guidelines

### Social Security Numbers
- **Required format**: 9 digits with no spaces or dashes
- **Accepted input**: `111-22-3333` or `111223333` (both converted to `111223333`)
- **Example**: `111223333`

### Dates
- **Accepted formats**: 
  - `MM/DD/YYYY` (e.g., `01/15/1985`)
  - `YYYYMMDD` (e.g., `19850115`)
- **Output format**: Always converted to `YYYYMMDD` for EDI
- **Examples**:
  - Input: `01/15/1985` → Output: `19850115`
  - Input: `20240101` → Output: `20240101`

### Gender Codes
- **Accepted values**: `M`, `Male`, `F`, `Female`, `U`, `Unknown`
- **Standardized to**: `M` (Male), `F` (Female), or `U` (Unknown)
- **Case-insensitive**

### State Codes
- **Format**: 2-letter state abbreviation (uppercase)
- **Examples**: `NY`, `CA`, `TX`, `FL`

### ZIP Codes
- **Formats**: 
  - 5-digit: `10001`
  - 9-digit: `10001-1234`
- **Both formats accepted**

### Relationship Codes
The system maps relationship values to EDI codes:

| Input Value | EDI Code | Description |
|-------------|----------|-------------|
| Employee, Self | 18 | Self |
| Spouse | 01 | Spouse |
| Child, Dependent | 19 | Child |

## Plan Codes

Valid plan codes must be configured in `edi834/config/validation_rules.yaml`. Default plan codes include:

- `MED001`, `MED002` - Medical plans
- `DENT001`, `DENT002` - Dental plans
- `VISION001`, `VISION002` - Vision plans
- `HSA001` - Health Savings Account
- `FSA001` - Flexible Spending Account

**Note**: You can add or modify plan codes in the configuration file to match your organization's plans.

## Sample CSV File

```csv
employee_id,ssn,first_name,last_name,middle_name,dob,gender,address1,address2,city,state,zip,plan_code,coverage_start,coverage_end,relationship
12345,111223333,John,Doe,Michael,01/15/1985,M,123 Main Street,Apt 4B,New York,NY,10001,MED001,01/01/2024,,Employee
23456,222334444,Jane,Smith,,03/22/1990,F,456 Oak Avenue,,Los Angeles,CA,90001,MED001,01/01/2024,,Employee
34567,333445555,Robert,Johnson,Lee,07/10/1978,M,789 Pine Road,Suite 100,Chicago,IL,60601,DENT001,01/01/2024,,Employee
```

## CSV File Requirements

### File Encoding
- **Recommended**: UTF-8
- **Supported**: UTF-8, ASCII

### Line Endings
- Unix (LF): `\n`
- Windows (CRLF): `\r\n`
- Mac (CR): `\r`

All line ending styles are supported.

### Header Row
- **Required**: First row must contain column headers
- **Case-insensitive**: Column names can be in any case
- **Whitespace**: Leading/trailing spaces in headers are trimmed

### Data Rows
- Each row represents one enrollment record
- Empty rows are skipped
- Whitespace in fields is automatically trimmed

## Validation

All input data is validated against the following rules:

1. **Required fields** must be present and non-empty
2. **SSN** must be exactly 9 digits
3. **Dates** must be valid dates in YYYYMMDD format
4. **Plan codes** must match configured valid codes
5. **Field lengths** must not exceed maximum lengths
6. **Coverage end date** must be after coverage start date (if both provided)
7. **State codes** must be valid 2-letter abbreviations
8. **ZIP codes** must be 5 or 9 digits

## Tips for Preparing CSV Files

1. **Export from Excel**: Save as "CSV UTF-8 (Comma delimited) (*.csv)"
2. **Remove extra columns**: Include only the columns listed in this specification
3. **Check for special characters**: Avoid using `*`, `~`, or `:` in text fields (they are EDI delimiters)
4. **Consistent date format**: Use the same date format throughout the file
5. **Clean data**: Remove leading/trailing spaces from all fields
6. **Test with sample**: Use the provided sample file to test your format

## Common Issues

### Issue: "Missing required field: ssn"
- **Cause**: SSN column is missing or empty
- **Solution**: Ensure every record has a valid SSN

### Issue: "Invalid SSN format"
- **Cause**: SSN has letters or incorrect number of digits
- **Solution**: SSN must be exactly 9 digits

### Issue: "Invalid date format"
- **Cause**: Date is not in MM/DD/YYYY or YYYYMMDD format
- **Solution**: Format dates consistently

### Issue: "Invalid plan code"
- **Cause**: Plan code doesn't match configured values
- **Solution**: Check `validation_rules.yaml` for valid plan codes, or add your plan code to the configuration

## Programmatic Access

You can also use the parser programmatically:

```python
from edi834.parser import parse_csv

# Parse CSV file
records = parse_csv('enrollment_data.csv')

# Access parsed data
for record in records:
    print(f"Employee: {record['first_name']} {record['last_name']}")
    print(f"SSN: {record['ssn']}")
    print(f"Plan: {record['plan_code']}")
```

## Next Steps

- Review [Validation Rules](validation_rules.md) for detailed validation criteria
- See [EDI Structure](edi_structure.md) to understand the output format
- Check [Troubleshooting](troubleshooting.md) for common issues and solutions
