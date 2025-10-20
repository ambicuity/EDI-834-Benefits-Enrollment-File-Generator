# EDI 834 Benefits Enrollment File Generator

[![CI](https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator/actions/workflows/ci.yml/badge.svg)](https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python-based ETL and EDI 834 generator that converts employee benefits enrollment data (CSV) into compliant ANSI X12 834 files.

---

## 🎯 Overview

The EDI 834 Benefits Enrollment File Generator simplifies the process of creating standardized benefit enrollment files for transmission to insurance carriers and benefits providers. It handles the complex EDI format so you don't have to.

### Key Features

- ✅ **Simple CSV Input**: Use familiar spreadsheet format
- 🔍 **Comprehensive Validation**: Catch errors before generating EDI
- 📋 **ANSI X12 Compliant**: Generates standard 005010X220A1 format
- 🎨 **User-Friendly CLI**: Beautiful console output with progress indicators
- 📊 **Flexible Reports**: Generate validation reports in text, JSON, or CSV
- ⚙️ **Configurable**: Customize validation rules and plan codes
- 🧪 **Well Tested**: Comprehensive test suite included

---

## 📚 Documentation

- [Overview](docs/overview.md) - Project overview and architecture
- [Input Specification](docs/input_specification.md) - CSV format requirements
- [EDI Structure](docs/edi_structure.md) - Understanding EDI 834 format
- [Validation Rules](docs/validation_rules.md) - Data validation requirements
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

---

## 🚀 Quick Start

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

### Basic Usage

```bash
# Generate EDI 834 file from CSV
python -m edi834.cli --input examples/sample_input.csv --output output/benefits_834.edi

# Validate data without generating EDI
python -m edi834.cli --input data.csv --validate-only

# Generate with validation report
python -m edi834.cli --input data.csv --output out.edi --validation-report report.txt

# Production mode (default is test)
python -m edi834.cli --input data.csv --output out.edi --production
```

### Command-Line Options

```bash
python -m edi834.cli --help
```

**Options**:
- `--input, -i`: Input CSV file with enrollment data (required)
- `--output, -o`: Output EDI 834 file path
- `--sender`: Sender ID (up to 15 characters, default: SENDER)
- `--receiver`: Receiver ID (up to 15 characters, default: RECEIVER)
- `--validate, --validate-only`: Only validate without generating EDI
- `--validation-report`: Save validation report to file
- `--production, -p`: Generate production file (default is test mode)
- `--pretty`: Pretty print EDI output with line breaks
- `--verbose, -v`: Verbose output

---

## 📝 CSV Input Format

Your CSV file should include these required fields:

| Field | Description | Example |
|-------|-------------|---------|
| `employee_id` | Unique employee identifier | `12345` |
| `ssn` | Social Security Number (9 digits) | `111223333` |
| `first_name` | First name | `John` |
| `last_name` | Last name | `Doe` |
| `dob` | Date of birth (MM/DD/YYYY or YYYYMMDD) | `01/15/1985` |
| `plan_code` | Benefit plan identifier | `MED001` |
| `coverage_start` | Coverage start date | `01/01/2024` |

**Optional fields**: `middle_name`, `gender`, `address1`, `address2`, `city`, `state`, `zip`, `coverage_end`, `relationship`, `subscriber_id`

See [Input Specification](docs/input_specification.md) for complete details.

---

## 📊 Sample Data

A sample CSV file is included in the `examples/` directory:

```csv
employee_id,ssn,first_name,last_name,dob,plan_code,coverage_start,relationship
12345,111223333,John,Doe,01/15/1985,MED001,01/01/2024,Employee
23456,222334444,Jane,Smith,03/22/1990,MED001,01/01/2024,Employee
```

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parser.py -v

# Run with coverage
pytest tests/ --cov=edi834 --cov-report=html
```

---

## ⚙️ Configuration

### Validation Rules

Edit `edi834/config/validation_rules.yaml` to customize:
- Required fields
- Valid plan codes
- Field length limits
- Validation patterns

### Adding Plan Codes

```yaml
# edi834/config/validation_rules.yaml
plan_codes:
  - MED001
  - MED002
  - YOUR_CUSTOM_CODE  # Add your plan codes here
```

---

## 🏗️ Project Structure

```
.
├── edi834/                  # Main package
│   ├── __init__.py
│   ├── parser.py           # CSV parsing
│   ├── validator.py        # Data validation
│   ├── generator.py        # EDI 834 generation
│   ├── formatter.py        # EDI formatting
│   ├── utils.py            # Utility functions
│   ├── cli.py              # Command-line interface
│   └── config/             # Configuration files
│       ├── segment_map.yaml
│       └── validation_rules.yaml
├── tests/                  # Test suite
├── examples/               # Sample files
├── docs/                   # Documentation
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator.git
cd EDI-834-Benefits-Enrollment-File-Generator
pip install -e .

# Run tests
pytest tests/

# Run linting
flake8 edi834/
```

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

## 📋 Use Cases

- **HR Departments**: Upload monthly enrollment changes to insurance carriers
- **Benefits Administrators**: Transmit enrollment data to multiple carriers
- **Payroll Providers**: Sync employee benefit elections with carriers
- **System Integrators**: Build automated enrollment workflows

---

## 🛠️ Troubleshooting

See [Troubleshooting Guide](docs/troubleshooting.md) for solutions to common issues.

### Quick Fixes

**"Missing required field: ssn"**
→ Ensure every record has a valid 9-digit SSN

**"Invalid date format"**
→ Use MM/DD/YYYY or YYYYMMDD format

**"Invalid plan code"**
→ Add your plan codes to `validation_rules.yaml`

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Ritesh Rana**

- GitHub: [@ambicuity](https://github.com/ambicuity)
- Repository: [EDI-834-Benefits-Enrollment-File-Generator](https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator)

---

## 🙏 Acknowledgments

- Built following ANSI X12 005010X220A1 standard
- Compliant with HIPAA transaction standards

---

## 📞 Support

- **Documentation**: See the [docs/](docs/) directory
- **Issues**: [GitHub Issues](https://github.com/ambicuity/EDI-834-Benefits-Enrollment-File-Generator/issues)
- **Examples**: Check the [examples/](examples/) directory

---

## 🗺️ Roadmap

Future enhancements:
- [ ] GUI front-end (Tkinter or Streamlit)
- [ ] Multi-plan file splitting by carrier
- [ ] Automatic SFTP upload to carriers
- [ ] Support for dependent/spouse enrollment
- [ ] EDI 834 file parsing (reverse direction)
- [ ] Additional EDI transaction sets (835, 837)

---

## ⭐ Show Your Support

Give a ⭐️ if this project helped you!