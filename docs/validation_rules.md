# Validation Rules

## Overview

The EDI 834 generator validates enrollment data before generating EDI files to ensure data quality and compliance. This document explains all validation rules enforced by the system.

## Validation Process

Validation occurs in multiple stages:

1. **CSV Structure Validation**: Ensures the file has proper headers and is readable
2. **Field Presence Validation**: Checks that all required fields are present
3. **Format Validation**: Verifies data formats (SSN, dates, etc.)
4. **Business Rule Validation**: Enforces business logic (date ranges, valid codes, etc.)
5. **EDI Structure Validation**: Confirms the generated EDI has proper structure

## Required Fields

These fields **must** be present and non-empty in every record:

| Field | Rule | Error Message |
|-------|------|---------------|
| `employee_id` | Must be present | "Missing required field: employee_id" |
| `ssn` | Must be present | "Missing required field: ssn" |
| `first_name` | Must be present | "Missing required field: first_name" |
| `last_name` | Must be present | "Missing required field: last_name" |
| `dob` | Must be present | "Missing required field: dob" |
| `plan_code` | Must be present | "Missing required field: plan_code" |
| `coverage_start` | Must be present | "Missing required field: coverage_start" |

## Format Validation Rules

### Social Security Number (SSN)

**Rule**: Must be exactly 9 digits

**Valid Examples**:
- `111223333`
- `111-22-3333` (automatically converted to `111223333`)

**Invalid Examples**:
- `12345` (too short)
- `1112233334` (too long)
- `11122333A` (contains letters)
- `111-22-333` (incorrect format)

**Pattern**: `^\d{9}$`

**Error Message**: "Invalid SSN format: {value}"

### Date Fields

**Rule**: Must be 8 digits in YYYYMMDD format

**Valid Examples**:
- `20240101`
- `19850115`
- `01/15/1985` (automatically converted to `19850115`)

**Invalid Examples**:
- `2024-01-01` (dashes not allowed)
- `01/15/85` (2-digit year)
- `2024/01/01` (wrong separator)
- `20240132` (invalid date - day 32)

**Pattern**: `^\d{8}$`

**Applies To**:
- Date of birth (`dob`)
- Coverage start date (`coverage_start`)
- Coverage end date (`coverage_end`)

**Error Message**: "Invalid date format for {field}: {value} (expected YYYYMMDD)"

### ZIP Code

**Rule**: Must be 5 digits or 5+4 digits

**Valid Examples**:
- `10001`
- `10001-1234`
- `100011234`

**Invalid Examples**:
- `1001` (too short)
- `ABCDE` (not numeric)

**Pattern**: `^\d{5}(-\d{4})?$`

**Error Message**: "Invalid ZIP code format: {value}"

### State Code

**Rule**: Must be a valid 2-letter US state code (uppercase)

**Valid Examples**:
- `NY`, `CA`, `TX`, `FL`

**Invalid Examples**:
- `New York` (full name)
- `ny` (lowercase, but automatically converted)
- `ZZ` (invalid state)

**Pattern**: `^[A-Z]{2}$`

**Error Message**: "Invalid state code: {value} (expected 2-letter state code)"

## Value Validation Rules

### Plan Code

**Rule**: Must match one of the configured valid plan codes

**Default Valid Codes**:
- `MED001`, `MED002` (Medical)
- `DENT001`, `DENT002` (Dental)
- `VISION001`, `VISION002` (Vision)
- `HSA001` (Health Savings Account)
- `FSA001` (Flexible Spending Account)

**Configuration**: Defined in `edi834/config/validation_rules.yaml`

**Customization**: You can add or modify plan codes in the configuration file

**Error Message**: "Invalid plan code: {value}"

### Gender Code

**Rule**: Must be one of the valid gender codes

**Valid Codes**:
- `M` (Male)
- `F` (Female)
- `U` (Unknown)

**Auto-conversion**:
- `Male` → `M`
- `Female` → `F`
- Anything else → `U`

**Error Message**: "Invalid gender code: {value}"

### Relationship Code

**Rule**: Must be one of the valid relationship codes

**Valid Codes**:
- `18` (Self/Employee)
- `01` (Spouse)
- `19` (Child/Dependent)
- `53` (Life Partner)

**Auto-mapping**:
- `Employee`, `Self` → `18`
- `Spouse` → `01`
- `Child`, `Dependent` → `19`

**Error Message**: "Invalid relationship code: {value}"

## Field Length Validation

Maximum lengths for text fields:

| Field | Maximum Length | Error Message |
|-------|----------------|---------------|
| `first_name` | 35 characters | "Field first_name exceeds maximum length of 35" |
| `last_name` | 60 characters | "Field last_name exceeds maximum length of 60" |
| `middle_name` | 25 characters | "Field middle_name exceeds maximum length of 25" |
| `address1` | 55 characters | "Field address1 exceeds maximum length of 55" |
| `address2` | 55 characters | "Field address2 exceeds maximum length of 55" |
| `city` | 30 characters | "Field city exceeds maximum length of 30" |
| `employee_id` | 20 characters | "Field employee_id exceeds maximum length of 20" |
| `subscriber_id` | 20 characters | "Field subscriber_id exceeds maximum length of 20" |

## Business Logic Validation

### Coverage Date Logic

**Rule**: Coverage end date must be after coverage start date (if both are provided)

**Valid Example**:
- Start: `20240101`
- End: `20241231`

**Invalid Example**:
- Start: `20240201`
- End: `20240101` (end before start)

**Error Message**: "Coverage start date ({start}) is after end date ({end})"

## Validation Report

After validation, a report is generated with the following information:

### Summary Statistics
- Total records processed
- Valid records count
- Invalid records count
- Overall validation status

### Detailed Errors
For each invalid record:
- Record number
- Row number (from CSV)
- Employee ID
- List of all errors found

### Example Validation Report (Text Format)

```
============================================================
VALIDATION REPORT
============================================================
Total Records: 5
Valid Records: 4
Invalid Records: 1

ERRORS:
------------------------------------------------------------

Record #3 (Row 4, Employee ID: 34567):
  - Missing required field: ssn
  - Invalid date format for dob: 07/10/78 (expected YYYYMMDD)
  - Invalid plan code: INVALID999

============================================================
```

## Validation Report Formats

The validation report can be generated in three formats:

### 1. Text Format (`.txt`)
Human-readable format with formatting

**Command**:
```bash
python -m edi834.cli --input data.csv --validation-report report.txt
```

### 2. JSON Format (`.json`)
Structured data format for programmatic processing

**Command**:
```bash
python -m edi834.cli --input data.csv --validation-report report.json
```

**Example**:
```json
{
  "total_records": 5,
  "valid_records": 4,
  "invalid_records": 1,
  "valid": false,
  "errors": [
    {
      "record": 3,
      "row_number": 4,
      "employee_id": "34567",
      "errors": [
        "Missing required field: ssn",
        "Invalid date format for dob: 07/10/78 (expected YYYYMMDD)"
      ]
    }
  ]
}
```

### 3. CSV Format (`.csv`)
Spreadsheet-compatible format for analysis

**Command**:
```bash
python -m edi834.cli --input data.csv --validation-report report.csv
```

**Example**:
```csv
Record,Row,Employee ID,Error
3,4,34567,"Missing required field: ssn"
3,4,34567,"Invalid date format for dob: 07/10/78 (expected YYYYMMDD)"
```

## Validation-Only Mode

You can validate data without generating an EDI file:

```bash
python -m edi834.cli --input enrollment.csv --validate-only
```

This is useful for:
- Testing data quality before processing
- Identifying data issues early
- Generating validation reports without EDI generation

## Bypassing Validation

**Warning**: It is **not recommended** to bypass validation, as invalid data will produce non-compliant EDI files that may be rejected by receivers.

The system does not support bypassing validation to ensure data quality and compliance.

## Configuring Validation Rules

Validation rules are configured in `edi834/config/validation_rules.yaml`:

```yaml
required_fields:
  - employee_id
  - ssn
  - first_name
  - last_name
  - dob
  - plan_code
  - coverage_start

plan_codes:
  - MED001
  - MED002
  - DENT001
  # Add your custom codes here

patterns:
  ssn: '^\d{9}$'
  date: '^\d{8}$'
  zip: '^\d{5}(-\d{4})?$'
  state: '^[A-Z]{2}$'

max_lengths:
  first_name: 35
  last_name: 60
  # Add custom length limits here
```

### Adding Custom Plan Codes

To add your organization's plan codes:

1. Open `edi834/config/validation_rules.yaml`
2. Add your plan codes under the `plan_codes` section:
   ```yaml
   plan_codes:
     - MED001
     - YOUR_PLAN_CODE
     - ANOTHER_CODE
   ```
3. Save the file

### Modifying Field Length Limits

To change maximum field lengths:

1. Open `edi834/config/validation_rules.yaml`
2. Modify or add entries under `max_lengths`:
   ```yaml
   max_lengths:
     first_name: 50  # Increase from 35 to 50
     custom_field: 100
   ```

## Common Validation Errors

### "Missing required field: ssn"
**Cause**: The SSN field is empty or not present in the CSV
**Solution**: Ensure every employee record has a valid SSN

### "Invalid SSN format: 12345"
**Cause**: SSN doesn't have exactly 9 digits
**Solution**: Provide SSN in format `111223333` or `111-22-3333`

### "Invalid date format for dob"
**Cause**: Date is not in YYYYMMDD format
**Solution**: Use format `YYYYMMDD` like `19850115` or `01/15/1985`

### "Invalid plan code: DENTAL1"
**Cause**: Plan code is not in the configured list
**Solution**: 
- Use a valid plan code from the configuration
- Or add your plan code to `validation_rules.yaml`

### "Coverage start date is after end date"
**Cause**: The coverage end date is before the start date
**Solution**: Correct the dates so end date is after start date

### "Field first_name exceeds maximum length"
**Cause**: The name is too long (>35 characters)
**Solution**: Shorten the name or use an abbreviation

## Validation Best Practices

1. **Validate Early**: Run validation before generating EDI files
2. **Fix Issues Promptly**: Address validation errors immediately
3. **Use Reports**: Save validation reports for documentation
4. **Test with Samples**: Test with small datasets first
5. **Configure Appropriately**: Customize validation rules for your needs
6. **Monitor Trends**: Track common validation errors over time

## Next Steps

- Review [Input Specification](input_specification.md) for CSV format details
- See [Troubleshooting](troubleshooting.md) for solutions to common issues
- Check [EDI Structure](edi_structure.md) to understand the output format
