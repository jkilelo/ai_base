#!/usr/bin/env python3
"""
Quick Demo: Show what the Code Extractor found in the Usage Guide

This script demonstrates the results of extracting code from EXTRACTOR_USAGE_GUIDE.md
and displays some of the extracted code blocks.
"""

import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent))

from code_extractor import GenericCodeExtractor


def show_extraction_results():
    """Show what the extractor found in the usage guide"""

    extractor = GenericCodeExtractor()
    guide_path = Path(__file__).parent / "EXTRACTOR_USAGE_GUIDE.md"

    if not guide_path.exists():
        print("❌ EXTRACTOR_USAGE_GUIDE.md not found!")
        return

    print("🔍 EXTRACTION RESULTS FROM EXTRACTOR_USAGE_GUIDE.md")
    print("=" * 65)

    # Extract all codes
    content = guide_path.read_text(encoding="utf-8")
    codes = extractor.extract(content)

    # Get statistics
    stats = extractor.get_statistics(codes)

    print(f"📊 SUMMARY:")
    print(f"   Total code blocks found: {stats['total']}")
    print(f"   Languages detected: {', '.join(stats['by_language'].keys())}")
    print(f"   Extraction methods: {', '.join(stats['by_extraction_method'].keys())}")
    print(f"   Average confidence: {stats['confidence_stats']['avg']:.3f}")

    # Show language breakdown
    print(f"\n📈 BY LANGUAGE:")
    for lang, count in sorted(
        stats["by_language"].items(), key=lambda x: x[1], reverse=True
    ):
        print(f"   {lang:<12}: {count:>2} blocks")

    # Show method breakdown
    print(f"\n🔧 BY EXTRACTION METHOD:")
    for method, count in sorted(
        stats["by_extraction_method"].items(), key=lambda x: x[1], reverse=True
    ):
        print(f"   {method:<18}: {count:>2} blocks")

    # Show confidence breakdown
    print(f"\n⭐ BY CONFIDENCE:")
    print(f"   High (≥0.9)     : {stats['high_confidence']:>2} blocks")
    print(f"   Medium (0.7-0.9): {stats['medium_confidence']:>2} blocks")
    print(f"   Low (<0.7)      : {stats['low_confidence']:>2} blocks")

    # Show some example Python code
    python_codes = [c for c in codes if c.language == "python"]
    if python_codes:
        print(f"\n🐍 PYTHON CODE EXAMPLES:")
        for i, code in enumerate(python_codes[:2], 1):
            print(f"\n   Example {i} (confidence: {code.confidence:.3f}):")
            print(f"   " + "─" * 50)
            lines = code.content.split("\n")
            for line_num, line in enumerate(lines[:5], 1):
                print(f"   {line_num:>2}: {line}")
            if len(lines) > 5:
                print(f"   ... ({len(lines)} total lines)")

    # Show some bash examples
    bash_codes = [c for c in codes if c.language in ["bash", "shell"]]
    if bash_codes:
        print(f"\n💻 SHELL/BASH EXAMPLES:")
        for i, code in enumerate(bash_codes[:3], 1):
            print(f"   {i}. {code.content.strip()}")

    # Show high-confidence blocks
    high_conf = [c for c in codes if c.confidence >= 0.9]
    if high_conf:
        print(f"\n⭐ HIGH-CONFIDENCE BLOCKS:")
        for code in high_conf[:3]:
            preview = code.content[:50].replace("\n", " ")
            if len(code.content) > 50:
                preview += "..."
            print(f"   {code.language:<10} ({code.confidence:.3f}): {preview}")

    print(f"\n✅ Found {len(codes)} code blocks in the usage guide!")
    print(f"   Run the other example scripts to see more detailed analysis.")


if __name__ == "__main__":
    show_extraction_results()
