# Code Extractor Examples

This directory contains practical examples demonstrating how to use the `GenericCodeExtractor` to extract code from the `EXTRACTOR_USAGE_GUIDE.md` file.

## 📁 Example Files

### 1. `simple_extractor_example.py` - Quick Start
A concise example showing basic extraction capabilities:
- Extract all code blocks from the usage guide
- Display statistics by programming language
- Show sample Python and bash code blocks
- Save Python code to individual files

**Run it:**
```bash
python simple_extractor_example.py
```

### 2. `extractor_example.py` - Comprehensive Demo
A detailed example showcasing advanced features:
- Full extraction and analysis workflow
- Multiple filtering strategies (language, confidence, length)
- Export to different formats (files, JSON, CSV)
- Command-line equivalents
- Specific extraction scenarios

**Run it:**
```bash
python extractor_example.py
```

### 3. `cli_examples.py` - Command Line Demonstrations
Shows various command-line usage patterns:
- Basic extraction with different options
- Filtering and export combinations
- Debug and quiet modes
- Practical use cases

**Run it:**
```bash
python cli_examples.py
```

**For help only:**
```bash
python cli_examples.py --help-only
```

## 🚀 Quick Start

1. **Simple extraction:**
   ```bash
   python simple_extractor_example.py
   ```

2. **See all command-line options:**
   ```bash
   python code_extractor.py --help
   ```

3. **Extract directly from usage guide:**
   ```bash
   python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --stats
   ```

## 🎯 Common Use Cases

### Extract Python Code Only
```bash
python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --language python --output python_examples/
```

### High-Quality Code Blocks
```bash
python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --min-confidence 0.9 --min-length 50
```

### Export for Analysis
```bash
# As JSON
python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --format json --output codes.json

# As CSV
python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --format csv --output codes.csv
```

### Debug Extraction Process
```bash
python code_extractor.py EXTRACTOR_USAGE_GUIDE.md --log-level DEBUG --stats
```

## 📊 Expected Results

When you run these examples on `EXTRACTOR_USAGE_GUIDE.md`, you should see:

- **~20-30 code blocks** extracted
- **Languages detected:** python, bash, json, html, css
- **Extraction methods:** triple_backtick, single_backtick, html_code
- **Confidence scores:** mostly 0.8-0.95 range

## 🔧 Customization

You can modify these examples to:

- **Change input source:** Replace `EXTRACTOR_USAGE_GUIDE.md` with any file
- **Adjust filters:** Modify language, confidence, or length thresholds
- **Add new export formats:** Extend the export functionality
- **Custom analysis:** Add your own statistics or processing logic

## 📝 Generated Output

The examples will create several output directories/files:

- `extracted_examples/` - Various export formats
- `extracted_python/` - Python code files only
- `premium_python/` - High-quality Python code
- `usage_guide_codes.json` - JSON export
- `usage_guide_codes.csv` - CSV export

## 🐛 Troubleshooting

1. **Import errors:** Make sure you're running from the `utils/` directory
2. **File not found:** Ensure `EXTRACTOR_USAGE_GUIDE.md` exists
3. **Permission errors:** Check write permissions for output directories
4. **No code found:** Try lowering `--min-confidence` threshold

## 💡 Tips

- Use `--stats` to see detailed extraction information
- Combine filters for targeted extraction: `--language python --min-confidence 0.8`
- Use `--log-level DEBUG` to see exactly what's happening
- Start with `simple_extractor_example.py` to understand the basics
- Check the generated JSON files to see full metadata structure

## 🔗 Related Files

- `code_extractor.py` - Main extractor implementation
- `EXTRACTOR_USAGE_GUIDE.md` - Complete usage documentation
- Generated output files - Examples of extracted code
