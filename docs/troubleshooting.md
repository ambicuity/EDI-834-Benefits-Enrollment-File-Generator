# Troubleshooting Guide

## Common Issues and Solutions

This guide helps you resolve common problems when using the EDI 834 Benefits Enrollment File Generator.

## Installation Issues

### Issue: "Module not found: edi834"

**Symptoms**:
```
ModuleNotFoundError: No module named 'edi834'
```

**Causes**:
- Package not installed
- Running from wrong directory

**Solutions**:
1. Install the package:
   ```bash
   pip install -e .
   ```

2. Verify installation:
   ```bash
   python -c "import edi834; print(edi834.__version__)"
   ```

3. Make sure you're in the project root directory

---

### Issue: "Command 'python' not found"

**Symptoms**:
```
bash: python: command not found
```

**Causes**:
- Python not installed
- Python command is `python3` instead of `python`

**Solutions**:
1. Check if Python 3 is installed:
   ```bash
   python3 --version
   ```

2. Use `python3` instead of `python`:
   ```bash
   python3 -m edi834.cli --input data.csv --output out.edi
   ```

3. Create an alias (optional):
   ```bash
   alias python=python3
   ```

---

### Issue: "pip: command not found"

**Symptoms**:
```
bash: pip: command not found
```

**Solutions**:
1. Try `pip3`:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Install pip:
   ```bash
   python3 -m ensurepip --upgrade
   ```

---

## CSV File Issues

### Issue: "CSV file not found"

**Symptoms**:
```
FileNotFoundError: CSV file not found: data.csv
```

**Causes**:
- File doesn't exist at the specified path
- Incorrect file path

**Solutions**:
1. Verify file exists:
   ```bash
   ls -l data.csv
   ```

2. Use absolute path:
   ```bash
   python -m edi834.cli --input /full/path/to/data.csv --output out.edi
   ```

3. Check current directory:
   ```bash
   pwd
   ls
   ```

---

### Issue: "CSV file has no headers"

**Symptoms**:
```
ValueError: CSV file has no headers
```

**Causes**:
- First row doesn't contain column names
- File is empty

**Solutions**:
1. Ensure first row has headers:
   ```csv
   employee_id,ssn,first_name,last_name,...
   12345,111223333,John,Doe,...
   ```

2. Check file isn't empty:
   ```bash
   head -n 5 data.csv
   ```

---

### Issue: "Error parsing row"

**Symptoms**:
```
Warning: Error parsing row 5: ...
```

**Causes**:
- Malformed CSV (extra commas, quotes)
- Special characters in data

**Solutions**:
1. Check the specific row in your CSV
2. Ensure fields with commas are quoted:
   ```csv
   "123 Main St, Apt 4B"
   ```
3. Remove special characters or escape them properly

---

## Validation Issues

### Issue: "Missing required field: ssn"

**Symptoms**:
```
Validation failed: Missing required field: ssn
```

**Causes**:
- SSN column missing from CSV
- SSN value is empty for some records

**Solutions**:
1. Add SSN column to CSV:
   ```csv
   employee_id,ssn,first_name,...
   ```

2. Fill in missing SSN values
3. Check for empty cells in Excel/spreadsheet

---

### Issue: "Invalid SSN format"

**Symptoms**:
```
Invalid SSN format: 12345
```

**Causes**:
- SSN has fewer or more than 9 digits
- SSN contains letters or special characters

**Solutions**:
1. Use 9-digit format:
   ```
   111223333  ✓ Correct
   111-22-3333  ✓ Correct (dashes removed automatically)
   12345  ✗ Incorrect (too short)
   ```

2. Remove letters/special characters
3. Use Excel formula to clean SSNs:
   ```excel
   =SUBSTITUTE(SUBSTITUTE(A1,"-","")," ","")
   ```

---

### Issue: "Invalid date format"

**Symptoms**:
```
Invalid date format for dob: 01/15/85 (expected YYYYMMDD)
```

**Causes**:
- 2-digit year
- Wrong separator (dash instead of slash)
- Invalid date value

**Solutions**:
1. Use 4-digit year:
   ```
   01/15/1985  ✓ Correct
   19850115  ✓ Correct
   01/15/85  ✗ Incorrect (2-digit year)
   ```

2. Excel formula to format dates:
   ```excel
   =TEXT(A1,"YYYYMMDD")
   ```

3. Check for invalid dates (e.g., February 30)

---

### Issue: "Invalid plan code"

**Symptoms**:
```
Invalid plan code: DENTAL1
```

**Causes**:
- Plan code not in configured list
- Typo in plan code

**Solutions**:
1. Check valid plan codes in `edi834/config/validation_rules.yaml`

2. Add your plan code to the configuration:
   ```yaml
   plan_codes:
     - MED001
     - DENTAL1  # Add your code here
   ```

3. Correct typos in CSV file

---

### Issue: "Coverage start date is after end date"

**Symptoms**:
```
Coverage start date (20240201) is after end date (20240101)
```

**Causes**:
- Dates entered in wrong order
- Typo in dates

**Solutions**:
1. Verify date logic:
   ```
   Start: 2024-01-01
   End:   2024-12-31  ✓ Correct
   
   Start: 2024-02-01
   End:   2024-01-01  ✗ Incorrect
   ```

2. Swap dates if reversed
3. Leave end date empty for ongoing coverage

---

## EDI Generation Issues

### Issue: "Cannot generate EDI file: validation errors found"

**Symptoms**:
```
Cannot generate EDI file: validation errors found
```

**Causes**:
- Input data has validation errors

**Solutions**:
1. Run validation-only mode to see all errors:
   ```bash
   python -m edi834.cli --input data.csv --validate-only
   ```

2. Generate validation report:
   ```bash
   python -m edi834.cli --input data.csv --validation-report errors.txt
   ```

3. Fix all validation errors before generating EDI

---

### Issue: "Output file required for EDI generation"

**Symptoms**:
```
Output file required for EDI generation (use --output)
```

**Causes**:
- Forgot to specify output file path

**Solutions**:
```bash
python -m edi834.cli --input data.csv --output benefits_834.edi
```

---

### Issue: "Permission denied" when writing output

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied: 'output.edi'
```

**Causes**:
- No write permission in directory
- File is open in another program
- Directory doesn't exist

**Solutions**:
1. Create output directory:
   ```bash
   mkdir -p output
   python -m edi834.cli --input data.csv --output output/file.edi
   ```

2. Check permissions:
   ```bash
   ls -la output/
   chmod 755 output/
   ```

3. Close file if open in Excel/text editor

---

## Runtime Issues

### Issue: "Unexpected error" with traceback

**Symptoms**:
```
Unexpected error: ...
[Long error traceback]
```

**Solutions**:
1. Run with verbose mode to see details:
   ```bash
   python -m edi834.cli --input data.csv --output out.edi --verbose
   ```

2. Check the specific error message in the traceback
3. Report the issue on GitHub with the full error

---

### Issue: "Out of memory" for large files

**Symptoms**:
```
MemoryError: Unable to allocate array
```

**Causes**:
- CSV file is very large (>100,000 rows)
- Insufficient system memory

**Solutions**:
1. Split CSV into smaller batches:
   ```bash
   # Unix/Mac
   split -l 10000 data.csv batch_
   
   # Windows
   # Use Excel to split file manually
   ```

2. Process each batch separately:
   ```bash
   python -m edi834.cli --input batch_aa --output out_1.edi
   python -m edi834.cli --input batch_ab --output out_2.edi
   ```

3. Increase available memory or use a machine with more RAM

---

## Output Issues

### Issue: "Generated EDI structure validation failed"

**Symptoms**:
```
Generated EDI structure validation failed:
  - Missing required segment: GS
```

**Causes**:
- Internal error in EDI generation
- Bug in the generator

**Solutions**:
1. Report the issue on GitHub with:
   - Input CSV file (anonymized if needed)
   - Command used
   - Error message

2. Try with a smaller sample file
3. Check for recent updates to the tool

---

### Issue: "Carrier rejects the EDI file"

**Symptoms**:
- File generates successfully
- Carrier reports validation errors

**Causes**:
- Carrier-specific requirements
- Additional segments needed
- Different EDI version required

**Solutions**:
1. Check carrier's EDI 834 specification document
2. Verify they accept version 005010X220A1
3. Contact carrier for specific requirements
4. Consider customizing the generator for carrier-specific needs

---

## Testing Issues

### Issue: "Test failed: ModuleNotFoundError"

**Symptoms**:
```
ModuleNotFoundError: No module named 'edi834'
```

**Causes**:
- Package not installed in development mode

**Solutions**:
```bash
pip install -e .
pytest tests/
```

---

### Issue: "Tests fail with file not found"

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'edi834/config/validation_rules.yaml'
```

**Causes**:
- Running tests from wrong directory

**Solutions**:
```bash
# Run from project root
cd /path/to/EDI-834-Benefits-Enrollment-File-Generator
pytest tests/
```

---

## Configuration Issues

### Issue: "Config file not found"

**Symptoms**:
```
FileNotFoundError: edi834/config/validation_rules.yaml
```

**Causes**:
- Configuration file missing
- Package not properly installed

**Solutions**:
1. Verify config files exist:
   ```bash
   ls -la edi834/config/
   ```

2. Reinstall package:
   ```bash
   pip install -e .
   ```

3. Check if files were accidentally deleted

---

## Performance Issues

### Issue: "Processing is very slow"

**Symptoms**:
- Tool takes a long time to process files

**Solutions**:
1. Check file size:
   ```bash
   wc -l data.csv  # Count rows
   ```

2. For large files (>50,000 rows), expect longer processing

3. Monitor system resources:
   ```bash
   top  # Unix/Mac
   # Task Manager on Windows
   ```

---

## Getting Help

If you can't find a solution here:

1. **Check Examples**:
   ```bash
   python -m edi834.cli --help
   ```

2. **Run with Verbose Mode**:
   ```bash
   python -m edi834.cli --input data.csv --output out.edi --verbose
   ```

3. **Review Documentation**:
   - [Input Specification](input_specification.md)
   - [Validation Rules](validation_rules.md)
   - [EDI Structure](edi_structure.md)

4. **Report Issues**:
   - GitHub Issues: https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator/issues
   - Include:
     - Error message
     - Command used
     - Sample data (anonymized)
     - System information (OS, Python version)

5. **Community Support**:
   - Check existing GitHub issues
   - Search for similar problems
   - Ask questions in discussions

---

## Preventive Measures

To avoid common issues:

1. **Validate Early**: Use `--validate-only` before generating
2. **Start Small**: Test with a few records first
3. **Use Examples**: Base your CSV on the sample file
4. **Keep Backups**: Save original CSV before modifications
5. **Document Changes**: Note any custom configuration changes
6. **Update Regularly**: Keep the tool updated to the latest version

---

## System Requirements

- **Python**: 3.8 or higher
- **Memory**: At least 512 MB RAM (more for large files)
- **Disk Space**: At least 100 MB free
- **Operating System**: Windows, macOS, or Linux

---

## Quick Reference

### Essential Commands

```bash
# Basic generation
python -m edi834.cli --input data.csv --output out.edi

# Validation only
python -m edi834.cli --input data.csv --validate-only

# With validation report
python -m edi834.cli --input data.csv --output out.edi --validation-report report.txt

# Production mode
python -m edi834.cli --input data.csv --output out.edi --production

# Custom sender/receiver
python -m edi834.cli --input data.csv --output out.edi --sender ACME --receiver INS
```

### File Locations

- Configuration: `edi834/config/`
- Examples: `examples/`
- Tests: `tests/`
- Documentation: `docs/`
