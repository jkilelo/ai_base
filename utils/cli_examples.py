#!/usr/bin/env python3
"""
Command Line Examples for Code Extractor

This script demonstrates various command-line usage patterns for the
GenericCodeExtractor when working with the EXTRACTOR_USAGE_GUIDE.md file.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and show the results"""
    print(f"\n🚀 {description}")
    print(f"💻 Command: {cmd}")
    print("-" * 60)

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")

        print(f"✅ Exit code: {result.returncode}")

    except Exception as e:
        print(f"❌ Failed to run command: {e}")


def main():
    """Demonstrate various command-line usage patterns"""

    guide_path = Path(__file__).parent / "EXTRACTOR_USAGE_GUIDE.md"

    if not guide_path.exists():
        print("❌ EXTRACTOR_USAGE_GUIDE.md not found!")
        return

    print("📚 Code Extractor Command Line Examples")
    print("=" * 70)
    print(f"📄 Source file: {guide_path}")

    # Example 1: Basic extraction
    run_command(
        f'python code_extractor.py "{guide_path}"',
        "Basic extraction - save all code blocks as individual files",
    )

    # Example 2: Extract with statistics
    run_command(
        f'python code_extractor.py "{guide_path}" --stats',
        "Show detailed statistics about extracted code",
    )

    # Example 3: Filter by language
    run_command(
        f'python code_extractor.py "{guide_path}" --language python --stats',
        "Extract only Python code blocks",
    )

    # Example 4: High confidence filtering
    run_command(
        f'python code_extractor.py "{guide_path}" --min-confidence 0.9 --stats',
        "Extract only high-confidence code blocks (≥0.9)",
    )

    # Example 5: Export as JSON
    run_command(
        f'python code_extractor.py "{guide_path}" --format json --output usage_guide_codes.json',
        "Export all code blocks as JSON",
    )

    # Example 6: Export as CSV
    run_command(
        f'python code_extractor.py "{guide_path}" --format csv --output usage_guide_codes.csv',
        "Export code blocks as CSV for analysis",
    )

    # Example 7: Filter by content length
    run_command(
        f'python code_extractor.py "{guide_path}" --min-length 50 --stats',
        "Extract only substantial code blocks (≥50 characters)",
    )

    # Example 8: Filter by content containing specific text
    run_command(
        f'python code_extractor.py "{guide_path}" --contains "import" --stats',
        "Extract code blocks containing 'import'",
    )

    # Example 9: Combine multiple filters
    run_command(
        f'python code_extractor.py "{guide_path}" --language python --min-confidence 0.8 --min-length 30 --output premium_python',
        "Premium Python code: high confidence + substantial size",
    )

    # Example 10: Debug mode with specific patterns
    run_command(
        f'python code_extractor.py "{guide_path}" --patterns triple_backtick single_backtick --log-level DEBUG --stats',
        "Debug mode with specific extraction patterns",
    )

    # Example 11: Quiet mode (errors only)
    run_command(
        f'python code_extractor.py "{guide_path}" --quiet --format json --output quiet_extraction.json',
        "Quiet mode - suppress all output except errors",
    )

    print("\n" + "=" * 70)
    print("✅ Command line examples complete!")
    print("\n📁 Generated files:")

    # List generated files
    for pattern in [
        "extracted_code/",
        "usage_guide_codes.*",
        "premium_python/",
        "quiet_extraction.json",
    ]:
        for file in Path(__file__).parent.glob(pattern):
            if file.is_file():
                print(f"   📄 {file.name}")
            elif file.is_dir():
                file_count = len(list(file.glob("*")))
                print(f"   📁 {file.name}/ ({file_count} files)")


def show_help():
    """Show the help for the code extractor"""
    run_command(
        "python code_extractor.py --help", "Code Extractor Help - All available options"
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--help-only":
        show_help()
    else:
        main()
