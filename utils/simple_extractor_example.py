#!/usr/bin/env python3
"""
Simple Example: Extract Code from Usage Guide

This is a concise example showing how to use the GenericCodeExtractor
to extract code from the EXTRACTOR_USAGE_GUIDE.md file.
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from code_extractor import GenericCodeExtractor


def simple_extraction_example():
    """Simple example of extracting code from the usage guide"""

    # Initialize the extractor
    extractor = GenericCodeExtractor()

    # Read the usage guide
    guide_path = Path(__file__).parent / "EXTRACTOR_USAGE_GUIDE.md"

    if not guide_path.exists():
        print("❌ EXTRACTOR_USAGE_GUIDE.md not found!")
        return

    print("📚 Reading EXTRACTOR_USAGE_GUIDE.md...")
    content = guide_path.read_text(encoding="utf-8")

    # Extract all code blocks
    print("🔍 Extracting code blocks...")
    codes = extractor.extract(content)

    print(f"✅ Found {len(codes)} code blocks!\n")

    # Show summary by language
    languages = {}
    for code in codes:
        languages[code.language] = languages.get(code.language, 0) + 1

    print("📊 Languages found:")
    for lang, count in sorted(languages.items()):
        print(f"   {lang}: {count} blocks")

    # Show some Python examples
    python_codes = [c for c in codes if c.language == "python"]

    if python_codes:
        print(f"\n🐍 Python examples ({len(python_codes)} found):")
        for i, code in enumerate(python_codes[:3], 1):
            print(f"\n   Example {i} (confidence: {code.confidence:.3f}):")
            lines = code.content.split("\n")[:2]  # First 2 lines
            for line in lines:
                print(f"      {line}")
            if len(code.content.split("\n")) > 2:
                print(f"      ... ({len(code.content.split('\n'))} total lines)")

    # Show bash/shell examples
    bash_codes = [c for c in codes if c.language in ["bash", "shell"]]
    if bash_codes:
        print(f"\n💻 Shell/Bash commands ({len(bash_codes)} found):")
        for code in bash_codes[:2]:
            print(f"   {code.content.strip()}")

    # Save Python code to files
    if python_codes:
        output_dir = Path(__file__).parent / "extracted_python"
        output_dir.mkdir(exist_ok=True)

        print(f"\n💾 Saving Python code to {output_dir}/")
        extractor.export(python_codes, "files", str(output_dir))
        print(f"   Saved {len(python_codes)} Python files")

    print(f"\n🎉 Extraction complete!")


if __name__ == "__main__":
    simple_extraction_example()
