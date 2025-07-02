#!/usr/bin/env python3
"""
Example: Using Code Extractor to Extract Code from EXTRACTOR_USAGE_GUIDE.md

This example demonstrates how to use the GenericCodeExtractor to extract code
from the usage guide markdown file, showing various extraction and filtering
capabilities.
"""

import json
import sys
from pathlib import Path

# Add the utils directory to path so we can import the extractor
sys.path.append(str(Path(__file__).parent))

from code_extractor import GenericCodeExtractor, setup_logging


def main():
    """Demonstrate code extraction from the usage guide"""

    # Setup logging to see what's happening
    setup_logging(level="INFO")

    # Create the extractor
    extractor = GenericCodeExtractor()

    # Path to the usage guide
    guide_path = Path(__file__).parent / "EXTRACTOR_USAGE_GUIDE.md"

    print("🔍 Code Extractor Example: Extracting from EXTRACTOR_USAGE_GUIDE.md")
    print("=" * 70)

    # Read the guide content
    if not guide_path.exists():
        print(f"❌ Guide file not found: {guide_path}")
        return

    guide_content = guide_path.read_text(encoding="utf-8")
    print(f"📄 Loaded guide content: {len(guide_content)} characters")

    # Extract all code blocks
    print("\n🚀 Extracting all code blocks...")
    all_codes = extractor.extract(guide_content, source_type="markdown")

    print(f"✅ Found {len(all_codes)} total code blocks")

    # Show basic statistics
    stats = extractor.get_statistics(all_codes)
    print(f"\n📊 Basic Statistics:")
    print(f"   Total blocks: {stats['total']}")
    print(f"   Languages detected: {list(stats['by_language'].keys())}")
    print(f"   Average confidence: {stats['confidence_stats']['avg']:.3f}")
    print(f"   High confidence (≥0.9): {stats['high_confidence']}")
    print(f"   Medium confidence (0.7-0.9): {stats['medium_confidence']}")
    print(f"   Low confidence (<0.7): {stats['low_confidence']}")

    # Demonstrate filtering by language
    print("\n🐍 Filtering Python code blocks...")
    python_codes = extractor.filter(all_codes, language="python")
    print(f"   Found {len(python_codes)} Python code blocks")

    # Show sample Python code blocks
    for i, code in enumerate(python_codes[:3], 1):
        print(f"\n   Python Block {i} (confidence: {code.confidence:.3f}):")
        print(f"   Method: {code.extraction_method}")
        preview = code.content[:100].replace("\n", "\\n")
        if len(code.content) > 100:
            preview += "..."
        print(f"   Preview: {preview}")

    # Demonstrate filtering by confidence
    print("\n⭐ Filtering high-confidence blocks (≥0.9)...")
    high_conf_codes = extractor.filter(all_codes, min_confidence=0.9)
    print(f"   Found {len(high_conf_codes)} high-confidence blocks")

    # Show extraction methods used
    print(f"\n🔧 Extraction methods used:")
    for method, count in stats["by_extraction_method"].items():
        print(f"   {method}: {count} blocks")

    # Demonstrate filtering by content length
    print(f"\n📏 Filtering substantial code blocks (≥50 characters)...")
    substantial_codes = extractor.filter(all_codes, min_length=50)
    print(f"   Found {len(substantial_codes)} substantial code blocks")

    # Combine multiple filters
    print(f"\n🎯 Combining filters: Python + High confidence + Substantial size...")
    premium_python = extractor.filter(
        all_codes, language="python", min_confidence=0.8, min_length=30
    )
    print(f"   Found {len(premium_python)} premium Python blocks")

    # Show detailed info for premium Python blocks
    for i, code in enumerate(premium_python, 1):
        print(f"\n   Premium Python Block {i}:")
        print(f"     Language: {code.language}")
        print(f"     Confidence: {code.confidence:.3f}")
        print(f"     Length: {len(code.content)} characters")
        print(f"     Method: {code.extraction_method}")
        print(f"     Content preview:")

        # Show first few lines of content
        lines = code.content.split("\n")[:3]
        for line in lines:
            print(f"       {line}")
        if len(code.content.split("\n")) > 3:
            print(f"       ... ({len(code.content.split('\n'))} total lines)")

    # Demonstrate export capabilities
    print(f"\n💾 Export demonstrations:")

    # Create output directory
    output_dir = Path(__file__).parent / "extracted_examples"
    output_dir.mkdir(exist_ok=True)

    # Export all codes as individual files
    print(f"   📁 Exporting all code blocks as individual files...")
    extractor.export(all_codes, "files", str(output_dir / "all_codes"))

    # Export Python codes as JSON
    if python_codes:
        print(f"   📋 Exporting Python codes as JSON...")
        extractor.export(python_codes, "json", str(output_dir / "python_codes.json"))

    # Export statistics as JSON
    print(f"   📈 Exporting statistics...")
    with open(output_dir / "extraction_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    # Export high-confidence codes as CSV
    if high_conf_codes:
        print(f"   📊 Exporting high-confidence codes as CSV...")
        extractor.export(
            high_conf_codes, "csv", str(output_dir / "high_confidence.csv")
        )

    print(
        f"\n✅ Example complete! Check the '{output_dir}' directory for exported files."
    )

    # Command line equivalent examples
    print(f"\n💻 Command Line Equivalents:")
    print(f"   # Extract all codes:")
    print(
        f'   python code_extractor.py "{guide_path}" --format files --output extracted_all/'
    )
    print(f"   ")
    print(f"   # Extract only Python with high confidence:")
    print(
        f'   python code_extractor.py "{guide_path}" --language python --min-confidence 0.8 --stats'
    )
    print(f"   ")
    print(f"   # Export as JSON with detailed logging:")
    print(
        f'   python code_extractor.py "{guide_path}" --format json --output codes.json --log-level DEBUG'
    )

    # Show some interesting findings
    print(f"\n🔍 Interesting Findings:")
    bash_codes = extractor.filter(all_codes, language="bash")
    if bash_codes:
        print(f"   📜 Found {len(bash_codes)} bash/shell commands")

    json_codes = extractor.filter(all_codes, language="json")
    if json_codes:
        print(f"   📋 Found {len(json_codes)} JSON examples")

    # Show content that contains specific terms
    api_codes = extractor.filter(all_codes, contains="json")
    if api_codes:
        print(f"   🔌 Found {len(api_codes)} code blocks mentioning 'json'")

    print(
        f"\n🎉 This example extracted {len(all_codes)} code blocks from the usage guide!"
    )
    print(f"   Languages: {', '.join(stats['by_language'].keys())}")
    print(f"   Methods: {', '.join(stats['by_extraction_method'].keys())}")


def demo_specific_extractions():
    """Demonstrate specific extraction scenarios"""

    print("\n" + "=" * 70)
    print("🎯 SPECIFIC EXTRACTION SCENARIOS")
    print("=" * 70)

    extractor = GenericCodeExtractor()

    # Scenario 1: Extract from inline documentation
    inline_doc = """
    The function `print("hello")` outputs text. For loops use:
    ```python
    for i in range(10):
        print(i)
    ```
    """

    print("📝 Scenario 1: Mixed inline and block code")
    codes = extractor.extract(inline_doc)
    for code in codes:
        print(
            f"   {code.extraction_method}: {code.language} ({len(code.content)} chars)"
        )

    # Scenario 2: Extract from HTML-like content
    html_content = """
    <p>Use <code>document.getElementById("test")</code> to select elements.</p>
    <pre>
    function example() {
        return "HTML example";
    }
    </pre>
    """

    print("\n🌐 Scenario 2: HTML with embedded code")
    codes = extractor.extract(html_content)
    for code in codes:
        print(
            f"   {code.extraction_method}: {code.language} (confidence: {code.confidence:.3f})"
        )

    # Scenario 3: Extract with specific patterns only
    print("\n🎯 Scenario 3: Using specific patterns only")
    guide_path = Path(__file__).parent / "EXTRACTOR_USAGE_GUIDE.md"
    if guide_path.exists():
        content = guide_path.read_text()

        # Only triple backticks
        triple_only = extractor.extract(content, patterns=["triple_backtick"])
        print(f"   Triple backticks only: {len(triple_only)} blocks")

        # Only inline code
        inline_only = extractor.extract(content, patterns=["single_backtick"])
        print(f"   Inline code only: {len(inline_only)} blocks")


if __name__ == "__main__":
    try:
        main()
        demo_specific_extractions()
    except KeyboardInterrupt:
        print("\n\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback

        traceback.print_exc()
