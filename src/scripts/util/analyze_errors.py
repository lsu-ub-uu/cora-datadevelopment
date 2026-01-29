"""
Script to analyze the errors_nordiska.txt log file and generate a report
grouped by error message with the number of records that failed that validation.
"""

import re
from collections import defaultdict
from typing import Dict, List, Tuple
import argparse
import sys


def extract_error_messages(line: str) -> List[str]:
    """
    Extract error messages from a log line.

    Handles both:
    - "Errors: [message1., message2]" format
    - "Exception: message" format
    """
    errors = []

    # Handle "Exception:" format
    exception_match = re.search(r"Exception:\s*(.+)$", line)
    if exception_match:
        return [exception_match.group(1).strip()]

    # Handle "Errors: [...]" format
    errors_match = re.search(r"Errors:\s*\[(.*)\]", line)
    if errors_match:
        errors_content = errors_match.group(1)
        # Split by ".," or "., " to separate multiple errors
        error_parts = re.split(r"\.,\s*", errors_content)
        for part in error_parts:
            # Clean up the error message
            clean_error = part.strip()
            if clean_error.endswith("."):
                clean_error = clean_error[:-1]
            if clean_error:
                errors.append(clean_error)

    return errors


def analyze_error_log(
    file_path: str,
) -> Tuple[Dict[str, int], Dict[str, List[str]], int, int, int]:
    """
    Analyze the error log file and return error counts.
    Only analyzes entries after the LAST occurrence of "==== Processing complete ====".

    Returns:
        - Dictionary mapping error messages to their counts
        - Dictionary mapping error messages to example record IDs
        - Total number of failed records
        - Total number of successful records
    """
    error_counts = defaultdict(int)
    error_examples = defaultdict(list)
    total_failed = 0
    total_classic = 0
    total_successful = 0

    # Read all lines first to find the last occurrence of "Processing complete"
    with open(file_path, "r", encoding="utf-8") as f:
        all_lines = f.readlines()

    # Find the last occurrence of "==== Processing complete ===="
    last_processing_complete_index = -1
    for i, line in enumerate(all_lines):
        if "==== Processing complete ====" in line.strip():
            last_processing_complete_index = i

    if last_processing_complete_index == -1:
        # No "Processing complete" found, return empty results
        print("❌ No 'Processing complete' marker found in the log file.")
        return (
            dict(error_counts),
            dict(error_examples),
            total_failed,
            total_classic,
            total_successful,
        )

    # Process only lines after the last "Processing complete"
    for line in all_lines[last_processing_complete_index + 1 :]:
        line = line.strip()

        # Count successful transformations
        if "✅" in line:
            total_successful += 1
            continue

        # Count classic quality transformations
        if "☣️" in line:
            total_classic += 1

            # Extract record ID from the line (format: "☣️ diva2:1234567 - ...")
            record_id_match = re.search(r"☣️\s+(diva2:\d+)", line)
            record_id = record_id_match.group(1) if record_id_match else "unknown"

            error_messages = extract_error_messages(line)
            for error_msg in error_messages:
                error_counts[error_msg] += 1
                # Keep up to 3 examples per error type
                if len(error_examples[error_msg]) < 3:
                    error_examples[error_msg].append(record_id)
            continue

        # Process failed transformations
        if "❌" in line and ("Errors:" in line or "Exception:" in line):
            total_failed += 1

            # Extract record ID from the line (format: "❌ diva2:1234567 - ...")
            record_id_match = re.search(r"❌\s+(diva2:\d+)", line)
            record_id = record_id_match.group(1) if record_id_match else "unknown"

            error_messages = extract_error_messages(line)
            for error_msg in error_messages:
                error_counts[error_msg] += 1
                # Keep up to 3 examples per error type
                if len(error_examples[error_msg]) < 3:
                    error_examples[error_msg].append(record_id)

    return (
        dict(error_counts),
        dict(error_examples),
        total_failed,
        total_classic,
        total_successful,
    )


def generate_report(
    error_counts: Dict[str, int],
    error_examples: Dict[str, List[str]],
    total_failed: int,
    total_classic: int,
    total_successful: int,
):
    """Generate and print the error analysis report."""

    print("=" * 80)
    print("LOG ANALYSIS REPORT")
    print("=" * 80)
    print()

    print(f"📊 SUMMARY:")
    print(f"   ✅ Successful migrations: {total_successful:,}")
    print(f"   ☣️ Classic quality migrations: {total_classic:,}")
    print(f"   ❌ Failed migrations: {total_failed:,}")
    print(
        f"   📈 Success rate: {total_successful/(total_successful+total_classic+total_failed)*100:.1f}%"
    )
    print()

    if(len(error_counts) > 0):
        print(f"🔍 ERROR BREAKDOWN:")
        print(f"   Total unique error types: {len(error_counts)}")
        print()

        # Sort errors by frequency (descending)
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)

        print("📋 ERRORS BY FREQUENCY:")
        print("-" * 80)

        

        for i, (error_msg, count) in enumerate(sorted_errors, 1):
            percentage = (count / (total_failed + total_classic)) * 100
            examples = error_examples.get(error_msg, [])
            examples_str = ", ".join(examples) if examples else "no examples"
            print(f"\n{i}. Error: {error_msg}")
            print(f"   Count: {count:,} records ({percentage:.1f}% of all failures)")
            print(f"   Examples: {examples_str}")

        print()
    print("=" * 80)


def analyze_and_print_report(log_file_path: str):
    try:
        print(f"🔍 Analyzing error log: {log_file_path}")

        error_counts, error_examples, total_failed, total_classic, total_successful = (
            analyze_error_log(log_file_path)
        )

        generate_report(
            error_counts, error_examples, total_failed, total_classic, total_successful
        )

    except FileNotFoundError:
        print(f"❌ Error: File '{log_file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error analyzing log file: {e}")
        sys.exit(1)


def main():
    """Main function to run the error analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze error log file and generate grouped error report"
    )
    parser.add_argument(
        "log_file",
        nargs="?",
        default="logs/outputs-import.log",
        help="Path to the error log file (default: outputs-import.log in logs/)",
    )

    args = parser.parse_args()

    analyze_and_print_report(args.log_file)


if __name__ == "__main__":
    main()
