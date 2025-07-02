# Code Extractor - Usage Guide

## Overview

The Code Extractor is a comprehensive, input-agnostic tool that can extract code from various input formats including JSON conversations, HTML, Markdown, XML, and plain text. It uses advanced pattern matching and language detection to provide high-confidence code extraction.

## Key Features

### 🎯 Input Agnostic
- **JSON**: Conversation data, API responses, structured data
- **HTML**: Web pages, documentation, embedded code
- **Markdown**: README files, documentation, blog posts  
- **XML**: Configuration files, SOAP responses, structured docs
- **Plain Text**: Any text containing code snippets

### 🔍 Advanced Extraction Patterns
- Triple backticks: ` ```language\ncode\n``` `
- Single backticks: `` `inline code` ``
- Fenced with tildes: `~~~language\ncode\n~~~`
- Indented code blocks (4+ spaces)
- HTML tags: `<code>`, `<pre>`, `<script>`, `<style>`
- Language comments: `// lang: python`
- Heredoc syntax: `<<LANG\ncode\nLANG`

### 🧠 Smart Language Detection
Automatically detects 25+ programming languages based on syntax patterns:
- Python, JavaScript, TypeScript, Java, C#, C++, Go, Rust
- HTML, CSS, SQL, Bash, PowerShell, PHP, Ruby, Swift
- JSON, YAML, XML, Dockerfile, Makefile, and more

### 📊 Confidence Scoring
Each extracted code block gets a confidence score (0.0-1.0) based on:
- Extraction method reliability
- Content length and characteristics  
- Language detection accuracy
- Pattern matching quality

### 🔧 Flexible Filtering
Filter results by:
- Programming language
- Source type (json, html, markdown, etc.)
- Extraction method
- Confidence threshold
- Content length (min/max)
- Text contains
- Message role (for conversations)

### 📤 Multiple Export Formats
- **Individual Files**: Save each code block as a separate file
- **JSON**: Structured data with full metadata
- **CSV**: Tabular format for analysis
- **Custom**: Extensible export system

## Quick Start

### Basic Usage

```python
from generic_code_extractor import GenericCodeExtractor

# Create extractor
extractor = GenericCodeExtractor()

# Extract from any input
codes = extractor.extract(your_input_data)

# Print results
for code in codes:
    print(f"{code.language}: {len(code.content)} chars (confidence: {code.confidence:.3f})")
```

### JSON Conversation Data

```python
# From file
codes = extractor.extract(json.load(open('conversation.json')))

# From string  
json_string = '{"role": "assistant", "content": "```python\\nprint(\\"hello\\")\\n```"}'
codes = extractor.extract(json_string)

# From structured data
conversation = [
    {"role": "user", "content": "Help with Python"},
    {"role": "assistant", "content": "```python\\ndef hello():\\n    print('world')\\n```"}
]
codes = extractor.extract(conversation)
```

### HTML Content

```python
html = """
<html>
<script>
function test() { return true; }
</script>
<p>Use <code>console.log()</code> for debugging</p>
</html>
"""
codes = extractor.extract(html)
```

### Markdown Content

```python
markdown = """
# Examples

```python
def example():
    return "hello"
```

Use `pip install package` to install.
"""
codes = extractor.extract(markdown)
```

## Advanced Usage

### Custom Filtering

```python
# Extract with minimum confidence
codes = extractor.extract(data, min_confidence=0.8)

# Filter results
python_codes = extractor.filter(codes, language='python')
long_codes = extractor.filter(codes, min_length=100)
assistant_codes = extractor.filter(codes, role='assistant')

# Chain filters
high_quality = extractor.filter(codes, language='python', min_confidence=0.9, min_length=50)
```

### Specific Patterns

```python
# Use only specific extraction patterns
codes = extractor.extract(data, patterns=['triple_backtick', 'html_code'])

# All available patterns:
# 'triple_backtick', 'single_backtick', 'indented_code', 'fenced_tilde'
# 'html_code', 'html_pre', 'script_tag', 'style_tag', 'heredoc', 'language_comment'
```

### Export Results

```python
# Save as individual files
extractor.export(codes, 'files', 'output_directory/')

# Export as JSON with metadata
extractor.export(codes, 'json', 'codes.json', include_metadata=True)

# Export as CSV for analysis
extractor.export(codes, 'csv', 'codes.csv')
```

### Statistics and Analysis

```python
stats = extractor.get_statistics(codes)
print(f"Total: {stats['total']}")
print(f"Languages: {stats['by_language']}")
print(f"Average confidence: {stats['confidence_stats']['avg']:.3f}")
print(f"High confidence (≥0.9): {stats['high_confidence']}")
```

## Command Line Interface

```bash
# Basic usage
python generic_code_extractor.py input.json

# With options
python generic_code_extractor.py conversation.json \
    --format files \
    --output extracted/ \
    --min-confidence 0.8 \
    --language python \
    --stats

# Available options:
# --input-type: auto, json, text, html, xml, markdown
# --patterns: specific extraction patterns to use
# --min-confidence: minimum confidence threshold
# --language: filter by programming language
# --min-length/max-length: content length filters
# --contains: filter by content containing text
# --format: files, json, csv
# --stats: show detailed statistics
```

## ExtractedCode Object

Each extracted code block is represented as an `ExtractedCode` object:

```python
@dataclass
class ExtractedCode:
    content: str              # The actual code content
    language: str             # Detected/specified language
    source_type: str          # Input type (json, html, etc.)
    extraction_method: str    # Pattern used for extraction
    confidence: float         # Confidence score (0.0-1.0)
    context: Dict[str, Any]   # Source context (line numbers, message index, etc.)
    metadata: Dict[str, Any]  # Additional metadata (match position, etc.)
```

## Integration Examples

### Process Chat Export

```python
# Extract code from ChatGPT/Claude export
with open('chat_export.json') as f:
    chat_data = json.load(f)

codes = extractor.extract(chat_data)
python_codes = extractor.filter(codes, language='python', min_confidence=0.8)

# Save Python code files
extractor.export(python_codes, 'files', 'python_snippets/')
```

### Web Scraping Integration

```python
import requests
from bs4 import BeautifulSoup

# Get webpage content
response = requests.get('https://example.com/tutorial')
html_content = response.text

# Extract code examples
codes = extractor.extract(html_content)
examples = extractor.filter(codes, min_length=50)

# Analyze
stats = extractor.get_statistics(examples)
print(f"Found {len(examples)} code examples in {len(stats['by_language'])} languages")
```

### Documentation Processing

```python
from pathlib import Path

# Process all markdown files in a directory
all_codes = []
for md_file in Path('docs/').glob('*.md'):
    content = md_file.read_text()
    codes = extractor.extract(content)
    all_codes.extend(codes)

# Export comprehensive results
extractor.export(all_codes, 'json', 'documentation_code.json')
stats = extractor.get_statistics(all_codes)
print(f"Documentation contains {stats['total']} code blocks")
```

## Tips for Best Results

1. **Use appropriate confidence thresholds**: 0.9+ for high-quality code, 0.7+ for general use
2. **Combine filters**: Chain language, length, and confidence filters for targeted extraction
3. **Check extraction methods**: Different patterns work better for different content types
4. **Validate results**: Review confidence scores and extracted content quality
5. **Export strategically**: Use JSON for analysis, files for direct use, CSV for reporting

The Code Extractor is designed to be your go-to tool for extracting code from any source - just pass in your data and let it handle the complexity!
