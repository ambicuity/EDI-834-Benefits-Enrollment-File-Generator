# EDI 834 Structure

## Understanding EDI 834 Format

EDI 834 (Benefit Enrollment and Maintenance) is a hierarchical transaction set that follows the ANSI X12 standard. This document explains the structure in plain English for both technical and non-technical users.

## What is EDI?

**EDI (Electronic Data Interchange)** is a standardized format for exchanging business documents between computer systems. Think of it as a universal language that different healthcare and benefits systems use to communicate.

## EDI 834 File Structure

An EDI 834 file is like a set of Russian nesting dolls, with each level containing the one below it:

```
📦 Interchange (ISA/IEA) - The shipping container
  └─ 📦 Functional Group (GS/GE) - The package
      └─ 📦 Transaction Set (ST/SE) - The document
          └─ 📄 Enrollment Data - The actual benefit information
```

### Visual Structure

```
ISA (Start of File)
  ├─ GS (Start of Group)
  │   ├─ ST (Start of Transaction)
  │   │   ├─ BGN (Beginning Segment)
  │   │   ├─ 1000A Loop (Sponsor/Employer)
  │   │   │   └─ NM1 (Sponsor Name)
  │   │   ├─ 2000 Loop (Member - repeats for each employee)
  │   │   │   ├─ INS (Insurance Information)
  │   │   │   ├─ REF (References)
  │   │   │   ├─ DTP (Dates)
  │   │   │   ├─ 2100A Loop (Member Name & Demographics)
  │   │   │   │   ├─ NM1 (Member Name & SSN)
  │   │   │   │   ├─ N3 (Address)
  │   │   │   │   ├─ N4 (City/State/ZIP)
  │   │   │   │   └─ DMG (Demographics - DOB, Gender)
  │   │   │   └─ 2300 Loop (Health Coverage)
  │   │   │       ├─ HD (Coverage Details)
  │   │   │       └─ DTP (Coverage Dates)
  │   │   └─ SE (End of Transaction)
  │   └─ GE (End of Group)
  └─ IEA (End of File)
```

## Segment Breakdown

### Header Segments

#### ISA - Interchange Control Header
**Purpose**: Identifies the sender and receiver of the file

**Plain English**: "This file is from Company A going to Company B"

**Example**:
```
ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *241020*1200*^*00501*000000001*0*T*:~
```

**Key Elements**:
- Sender ID (padded to 15 characters)
- Receiver ID (padded to 15 characters)
- Date and time of transmission
- Control number (unique identifier)
- Test indicator (`T` = test, `P` = production)

#### GS - Functional Group Header
**Purpose**: Groups related transaction sets together

**Plain English**: "This package contains benefit enrollment documents"

**Example**:
```
GS*BE*SENDER*RECEIVER*20241020*1200*1*X*005010X220A1~
```

**Key Elements**:
- `BE` = Benefit Enrollment type
- Sender/Receiver codes
- Date and time
- Version number

#### ST - Transaction Set Header
**Purpose**: Marks the beginning of a benefit enrollment transaction

**Plain English**: "Here starts one benefit enrollment document"

**Example**:
```
ST*834*0001*005010X220A1~
```

### Control Segments

#### BGN - Beginning Segment
**Purpose**: Provides context for the entire transaction

**Plain English**: "This is a new/original enrollment submission dated..."

**Example**:
```
BGN*00*0001*20241020*120000*ET***4~
```

**Key Elements**:
- Transaction purpose (00 = Original)
- Reference number
- Date and time

### Sponsor Information (1000A Loop)

#### NM1 - Sponsor Name
**Purpose**: Identifies the employer/plan sponsor

**Plain English**: "The employer sponsoring these benefits is..."

**Example**:
```
NM1*P5*2*ACME CORPORATION*****FI*123456789~
```

**Key Elements**:
- `P5` = Plan Sponsor entity type
- Organization name
- Federal Tax ID

### Member Information (2000 Loop)

This loop repeats for each enrolled employee/member.

#### INS - Insured Benefit
**Purpose**: Indicates the member's insurance relationship and status

**Plain English**: "This person is enrolling as an employee/spouse/child with active coverage"

**Example**:
```
INS*Y*18*021*01*A***FT~
```

**Key Elements**:
- `Y` = Information applies to this person
- `18` = Self/Employee relationship
- `021` = Change maintenance type
- `A` = Active benefit status
- `FT` = Full-time employment

#### REF - Reference Numbers
**Purpose**: Provides subscriber and member IDs

**Plain English**: "This employee's ID is... their member number is..."

**Examples**:
```
REF*0F*SUB123456~    (Subscriber number)
REF*1L*EMP12345~     (Group/Policy number)
```

#### DTP - Date/Time Periods
**Purpose**: Specifies coverage effective and termination dates

**Plain English**: "Coverage starts on... and ends on..."

**Examples**:
```
DTP*348*D8*20240101~    (Coverage begin date)
DTP*349*D8*20241231~    (Coverage end date)
```

### Member Demographics (2100A Loop)

#### NM1 - Member Name
**Purpose**: Member's name and SSN

**Plain English**: "The member's name is John Michael Doe, SSN 111-22-3333"

**Example**:
```
NM1*IL*1*DOE*JOHN*M***34*111223333~
```

**Key Elements**:
- `IL` = Insured/Subscriber
- `1` = Person (not organization)
- Last name, First name, Middle name
- `34` = SSN identifier
- Social Security Number

#### N3 - Address Line
**Purpose**: Member's street address

**Plain English**: "The member lives at..."

**Example**:
```
N3*123 MAIN STREET*APT 4B~
```

#### N4 - City, State, ZIP
**Purpose**: Member's city, state, and postal code

**Plain English**: "In New York, NY 10001"

**Example**:
```
N4*NEW YORK*NY*10001~
```

#### DMG - Demographics
**Purpose**: Date of birth and gender

**Plain English**: "Born on January 15, 1985, Male"

**Example**:
```
DMG*D8*19850115*M~
```

**Key Elements**:
- `D8` = Date format (CCYYMMDD)
- Date of birth
- Gender code (`M`/`F`/`U`)

### Health Coverage (2300 Loop)

#### HD - Health Coverage
**Purpose**: Describes the benefit plan

**Plain English**: "Enrolled in Medical plan MED001 at Employee-only coverage level"

**Example**:
```
HD*021**HLT*MED001*EMP~
```

**Key Elements**:
- `021` = Change maintenance type
- `HLT` = Health insurance line
- Plan code
- Coverage level (EMP = Employee only, FAM = Family, etc.)

#### DTP - Coverage Dates
**Purpose**: Coverage effective dates for this specific plan

**Example**:
```
DTP*348*D8*20240101~
```

### Trailer Segments

#### SE - Transaction Set Trailer
**Purpose**: Marks the end of the transaction and counts segments

**Plain English**: "This transaction had 25 segments, control number 0001"

**Example**:
```
SE*25*0001~
```

#### GE - Functional Group Trailer
**Purpose**: Ends the functional group and counts transactions

**Plain English**: "This package contained 1 document, group number 1"

**Example**:
```
GE*1*1~
```

#### IEA - Interchange Control Trailer
**Purpose**: Ends the entire file

**Plain English**: "End of file, contained 1 group, control number 000000001"

**Example**:
```
IEA*1*000000001~
```

## Delimiters

EDI uses special characters to separate data:

- `*` (asterisk) - **Element Separator**: Separates fields within a segment
- `~` (tilde) - **Segment Terminator**: Marks the end of a segment
- `:` (colon) - **Component Separator**: Separates sub-elements (rarely used in 834)
- `^` (caret) - **Repetition Separator**: Separates repeated elements

## Complete Example

Here's a simple EDI 834 file for one employee:

```
ISA*00*          *00*          *ZZ*SENDER         *ZZ*RECEIVER       *241020*1200*^*00501*000000001*0*T*:~
GS*BE*SENDER*RECEIVER*20241020*1200*1*X*005010X220A1~
ST*834*0001*005010X220A1~
BGN*00*0001*20241020*120000*ET***4~
REF*38*0001~
DTP*007*D8*20241020~
NM1*P5*2*ACME CORPORATION*****FI*123456789~
INS*Y*18*021*01*A***FT~
REF*0F*EMP12345~
DTP*348*D8*20240101~
NM1*IL*1*DOE*JOHN*M***34*111223333~
N3*123 MAIN STREET*APT 4B~
N4*NEW YORK*NY*10001~
DMG*D8*19850115*M~
HD*021**HLT*MED001*EMP~
DTP*348*D8*20240101~
SE*16*0001~
GE*1*1~
IEA*1*000000001~
```

## How the Generator Creates This

1. **Reads CSV**: Gets employee data from your CSV file
2. **Validates**: Checks all data is correct and complete
3. **Builds Header**: Creates ISA, GS, ST segments with control numbers
4. **Adds Sponsor**: Creates sponsor loop with employer information
5. **Processes Members**: For each employee, creates:
   - INS segment (enrollment info)
   - REF segments (IDs)
   - DTP segments (dates)
   - NM1 segment (name and SSN)
   - N3/N4 segments (address)
   - DMG segment (demographics)
   - HD segment (coverage)
6. **Builds Trailer**: Creates SE, GE, IEA segments with counts
7. **Validates**: Ensures structure is correct

## Standards and Compliance

This generator creates files compliant with:
- **ANSI X12 005010X220A1**: The EDI 834 implementation guide version
- **HIPAA**: Follows HIPAA transaction standards for benefit enrollment

## Next Steps

- Review [Validation Rules](validation_rules.md) for data requirements
- Check [Troubleshooting](troubleshooting.md) for common issues
- See [Input Specification](input_specification.md) for CSV format details
