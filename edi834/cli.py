"""
Command-Line Interface for EDI 834 Generator.

Provides an easy-to-use CLI for HR/benefits teams to generate EDI 834 files.
"""

import argparse
import sys
import os
from datetime import datetime
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .parser import parse_csv, validate_csv_structure
from .validator import validate_records, generate_validation_report, save_validation_report
from .generator import generate_834
from .formatter import pretty_print_edi, validate_edi_structure


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='EDI 834 Benefits Enrollment File Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate EDI 834 file from CSV
  python -m edi834.cli --input data/enrollment.csv --output output/benefits_834.edi
  
  # Validate only (no file generation)
  python -m edi834.cli --input data/enrollment.csv --validate-only
  
  # Generate with custom sender/receiver IDs
  python -m edi834.cli --input data.csv --output out.edi --sender ACME001 --receiver INS999
  
  # Production mode (default is test)
  python -m edi834.cli --input data.csv --output out.edi --production
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input CSV file with enrollment data'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output EDI 834 file path'
    )
    
    parser.add_argument(
        '--sender',
        default='SENDER',
        help='Sender ID (up to 15 characters)'
    )
    
    parser.add_argument(
        '--receiver',
        default='RECEIVER',
        help='Receiver ID (up to 15 characters)'
    )
    
    parser.add_argument(
        '--validate', '--validate-only',
        action='store_true',
        dest='validate_only',
        help='Only validate the input file without generating EDI'
    )
    
    parser.add_argument(
        '--validation-report',
        help='Save validation report to file (text, json, or csv format based on extension)'
    )
    
    parser.add_argument(
        '--production', '-p',
        action='store_true',
        help='Generate production file (default is test mode)'
    )
    
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print EDI output with line breaks'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Initialize console
    if RICH_AVAILABLE:
        console = Console()
    else:
        console = None
    
    try:
        # Print header
        print_header(console)
        
        # Validate input file exists
        if not os.path.exists(args.input):
            print_error(console, f"Input file not found: {args.input}")
            return 1
        
        # Step 1: Validate CSV structure
        print_step(console, "Step 1: Validating CSV structure")
        csv_validation = validate_csv_structure(args.input)
        
        if not csv_validation['valid']:
            print_error(console, "CSV validation failed:")
            for error in csv_validation['errors']:
                print_error(console, f"  - {error}")
            return 1
        
        print_success(console, f"CSV structure valid: {csv_validation['row_count']} rows, "
                              f"{len(csv_validation['headers'])} columns")
        
        if args.verbose:
            print_info(console, f"Headers: {', '.join(csv_validation['headers'])}")
        
        # Step 2: Parse CSV
        print_step(console, "Step 2: Parsing enrollment data")
        records = parse_csv(args.input)
        print_success(console, f"Parsed {len(records)} enrollment records")
        
        # Step 3: Validate records
        print_step(console, "Step 3: Validating enrollment records")
        validation_results = validate_records(records)
        
        # Display validation results
        display_validation_results(console, validation_results, args.verbose)
        
        # Save validation report if requested
        if args.validation_report:
            report_format = 'text'
            if args.validation_report.endswith('.json'):
                report_format = 'json'
            elif args.validation_report.endswith('.csv'):
                report_format = 'csv'
            
            save_validation_report(validation_results, args.validation_report, report_format)
            print_success(console, f"Validation report saved to: {args.validation_report}")
        
        # Stop here if validate-only mode
        if args.validate_only:
            print_info(console, "Validation complete. Skipping EDI generation (--validate-only mode)")
            return 0 if validation_results['valid'] else 1
        
        # Check if validation passed
        if not validation_results['valid']:
            print_error(console, "Cannot generate EDI file: validation errors found")
            print_info(console, "Use --validate-only to see detailed validation report")
            return 1
        
        # Check output file specified
        if not args.output:
            print_error(console, "Output file required for EDI generation (use --output)")
            return 1
        
        # Step 4: Generate EDI 834
        print_step(console, "Step 4: Generating EDI 834 file")
        test_mode = not args.production
        
        edi_content = generate_834(
            records,
            sender_id=args.sender,
            receiver_id=args.receiver,
            test_mode=test_mode
        )
        
        # Pretty print if requested
        if args.pretty:
            edi_content = pretty_print_edi(edi_content)
        
        # Validate EDI structure
        edi_validation = validate_edi_structure(edi_content)
        if not edi_validation['valid']:
            print_error(console, "Generated EDI structure validation failed:")
            for error in edi_validation['errors']:
                print_error(console, f"  - {error}")
            return 1
        
        print_success(console, f"EDI 834 generated successfully ({edi_validation['segment_count']} segments)")
        
        # Step 5: Save output
        print_step(console, "Step 5: Saving EDI file")
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(edi_content)
        
        print_success(console, f"EDI file saved to: {args.output}")
        
        # Print summary
        print_summary(console, {
            'input_file': args.input,
            'output_file': args.output,
            'records_processed': len(records),
            'mode': 'Production' if args.production else 'Test',
            'sender_id': args.sender,
            'receiver_id': args.receiver,
        })
        
        return 0
        
    except KeyboardInterrupt:
        print_error(console, "\nOperation cancelled by user")
        return 130
    except Exception as e:
        print_error(console, f"Unexpected error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def print_header(console):
    """Print CLI header."""
    if console:
        console.print("\n[bold cyan]EDI 834 Benefits Enrollment File Generator[/bold cyan]")
        console.print("[dim]Author: Ritesh Rana[/dim]\n")
    else:
        print("\n" + "="*60)
        print("EDI 834 Benefits Enrollment File Generator")
        print("Author: Ritesh Rana")
        print("="*60 + "\n")


def print_step(console, message):
    """Print step message."""
    if console:
        console.print(f"\n[bold blue]→[/bold blue] {message}")
    else:
        print(f"\n→ {message}")


def print_success(console, message):
    """Print success message."""
    if console:
        console.print(f"[green]✓[/green] {message}")
    else:
        print(f"✓ {message}")


def print_error(console, message):
    """Print error message."""
    if console:
        console.print(f"[red]✗[/red] {message}", file=sys.stderr)
    else:
        print(f"✗ {message}", file=sys.stderr)


def print_info(console, message):
    """Print info message."""
    if console:
        console.print(f"[dim]{message}[/dim]")
    else:
        print(f"  {message}")


def display_validation_results(console, results, verbose=False):
    """Display validation results."""
    if results['valid']:
        print_success(console, f"All {results['valid_records']} records validated successfully")
    else:
        print_error(console, f"Validation failed: {results['invalid_records']} of {results['total_records']} records have errors")
        
        if verbose and results['errors']:
            print_info(console, "\nValidation errors:")
            for error_entry in results['errors'][:5]:  # Show first 5
                print_info(console, f"\n  Record #{error_entry['record']} (Employee: {error_entry['employee_id']}):")
                for error in error_entry['errors']:
                    print_info(console, f"    - {error}")
            
            if len(results['errors']) > 5:
                print_info(console, f"\n  ... and {len(results['errors']) - 5} more errors")
                print_info(console, "  Use --validation-report to see all errors")


def print_summary(console, summary):
    """Print execution summary."""
    if console:
        console.print("\n[bold green]✓ Generation Complete[/bold green]\n")
        
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Input File", summary['input_file'])
        table.add_row("Output File", summary['output_file'])
        table.add_row("Records Processed", str(summary['records_processed']))
        table.add_row("Mode", summary['mode'])
        table.add_row("Sender ID", summary['sender_id'])
        table.add_row("Receiver ID", summary['receiver_id'])
        table.add_row("Timestamp", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        console.print(table)
        console.print()
    else:
        print("\n" + "="*60)
        print("✓ Generation Complete")
        print("="*60)
        print(f"Input File:         {summary['input_file']}")
        print(f"Output File:        {summary['output_file']}")
        print(f"Records Processed:  {summary['records_processed']}")
        print(f"Mode:               {summary['mode']}")
        print(f"Sender ID:          {summary['sender_id']}")
        print(f"Receiver ID:        {summary['receiver_id']}")
        print(f"Timestamp:          {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")


if __name__ == '__main__':
    sys.exit(main())
