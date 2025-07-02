#!/usr/bin/env python3
"""
Code Extractor Examples - Complete Guide

This script provides an overview of all the example scripts and demonstrates
how to use the GenericCodeExtractor with the EXTRACTOR_USAGE_GUIDE.md file.
"""

import sys
from pathlib import Path


def show_examples_overview():
    """Show overview of all example scripts"""

    print("📚 CODE EXTRACTOR EXAMPLES - COMPLETE GUIDE")
    print("=" * 70)

    examples = [
        {
            "file": "simple_extractor_example.py",
            "title": "🚀 Quick Start Example",
            "description": "Basic extraction with minimal code",
            "features": [
                "Extract all code blocks",
                "Show language statistics",
                "Display sample code",
                "Save Python files",
            ],
        },
        {
            "file": "extractor_example.py",
            "title": "🔬 Comprehensive Demo",
            "description": "Full-featured example showing all capabilities",
            "features": [
                "Advanced filtering strategies",
                "Multiple export formats",
                "Debug logging demonstration",
                "Command-line equivalents",
                "Statistical analysis",
            ],
        },
        {
            "file": "show_results.py",
            "title": "📊 Results Overview",
            "description": "Quick view of extraction results",
            "features": [
                "Summary statistics",
                "Language breakdown",
                "Method analysis",
                "Sample code display",
            ],
        },
        {
            "file": "cli_examples.py",
            "title": "💻 Command Line Demo",
            "description": "Shows various CLI usage patterns",
            "features": [
                "Multiple CLI scenarios",
                "Filter combinations",
                "Export format examples",
                "Debug and quiet modes",
            ],
        },
    ]

    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print(f"   File: {example['file']}")
        print(f"   {example['description']}")
        print(f"   Features:")
        for feature in example["features"]:
            print(f"     • {feature}")

    print(f"\n" + "=" * 70)
    print("📋 QUICK COMMANDS TO TRY:")
    print("=" * 70)

    commands = [
        ("python simple_extractor_example.py", "Quick start - basic extraction"),
        ("python show_results.py", "See what was extracted"),
        (
            "python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --stats",
            "CLI with statistics",
        ),
        (
            "python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --language python",
            "Python only",
        ),
        (
            "python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --min-confidence 0.9",
            "High confidence",
        ),
        ("python code_extractor.py --help", "See all options"),
    ]

    for cmd, desc in commands:
        print(f"\n💻 {cmd}")
        print(f"   {desc}")

    print(f"\n" + "=" * 70)
    print("🎯 WHAT YOU'LL FIND IN EXTRACTOR_USAGE_GUIDE.md:")
    print("=" * 70)

    findings = [
        "~50 total code blocks",
        "5 Python examples (import statements, functions, classes)",
        "6 CSS snippets (selectors, properties)",
        "35 text blocks (inline code, commands)",
        "1 YAML configuration example",
        "1 Scala code snippet",
        "Multiple extraction methods: triple backticks, inline, indented",
        "Confidence scores from 0.49 to 1.00",
        "Real-world usage patterns",
    ]

    for finding in findings:
        print(f"   • {finding}")

    print(f"\n" + "=" * 70)
    print("📁 OUTPUT DIRECTORIES CREATED:")
    print("=" * 70)

    output_dirs = [
        ("extracted_code/", "All extracted code as individual files"),
        ("extracted_python/", "Python code files only"),
        ("extracted_examples/", "Various export format examples"),
    ]

    utils_dir = Path(__file__).parent
    for dir_name, description in output_dirs:
        dir_path = utils_dir / dir_name
        if dir_path.exists():
            file_count = len(list(dir_path.glob("*"))) if dir_path.is_dir() else 0
            print(f"   📁 {dir_name:<20} {description} ({file_count} files)")
        else:
            print(f"   📁 {dir_name:<20} {description} (not created yet)")

    print(f"\n✨ Ready to explore? Start with: python simple_extractor_example.py")


if __name__ == "__main__":
    show_examples_overview()
