# Example Applications - AI Base Platform

🎯 **Ready-to-use examples to kickstart your AI app development**

This directory contains complete example applications demonstrating different patterns and capabilities of the AI Base platform.

## 📂 Available Examples

| Example                               | Complexity     | Description                                    | Tech Used                 |
| ------------------------------------- | -------------- | ---------------------------------------------- | ------------------------- |
| **[Text Analyzer](text-analyzer/)**   | 🟢 Beginner     | Analyze text sentiment, readability, and style | LLM, TextStat, React      |
| **[Data Processor](data-processor/)** | 🟡 Intermediate | CSV analysis with AI insights and charts       | Pandas, LLM, Plotly       |
| **[Web Scraper](web-scraper/)**       | 🔴 Advanced     | Intelligent web content extraction             | BeautifulSoup, LLM, Async |

## 🚀 Quick Start with Examples

### 1. Copy Example to Your Apps Directory

```bash
# Choose an example and copy it
cp -r docs/examples/text-analyzer apps/my-text-analyzer
cd apps/my-text-analyzer

# Customize the config
notepad config.yaml
```

### 2. Register the Plugin

```python
# main.py (add to existing registrations)
from apps.my-text-analyzer.plugin import TextAnalyzerPlugin

# Register the plugin
text_analyzer = TextAnalyzerPlugin()
await text_analyzer.initialize()
app.include_router(text_analyzer.router, prefix="/api/v1/text-analyzer", tags=["Text Analyzer"])
```

### 3. Test and Customize

```bash
# Restart backend to load your new plugin
.\start_backend.ps1

# Test at http://localhost:8000/docs
# Look for your plugin's endpoints
```

## 📖 Example Breakdown

### Text Analyzer (Beginner)

**What it does:**
- Analyzes text for sentiment, tone, and readability
- Provides AI-powered insights and suggestions
- Shows basic statistics (word count, reading time)

**Key learning points:**
- Simple plugin structure
- LLM integration basics
- Error handling patterns
- React component creation

**Files:**
```text
text-analyzer/
├── plugin.py          # Main plugin class
├── config.yaml        # Configuration
├── handlers/
│   ├── processor.py   # Text analysis logic
│   └── api.py        # REST endpoints
└── frontend/
    └── TextAnalyzer.tsx  # React component
```

### Data Processor (Intermediate)

**What it does:**
- Uploads and analyzes CSV files
- Generates AI-powered insights about data patterns
- Creates interactive charts and visualizations
- Tracks analysis jobs and results

**Key learning points:**
- File upload handling
- Database integration
- Background task processing
- Chart generation
- Complex React UI

**Files:**
```text
data-processor/
├── plugin.py          # Main plugin class
├── config.yaml        # Configuration
├── models.py          # Database models
├── handlers/
│   ├── processor.py   # Data analysis engine
│   ├── api.py        # REST endpoints
│   └── charts.py     # Visualization logic
└── frontend/
    └── DataProcessor.tsx # React dashboard
```

### Web Scraper (Advanced)

**What it does:**
- Scrapes web content intelligently
- Extracts structured data using AI
- Handles different content types
- Provides content analysis and summarization

**Key learning points:**
- Async web scraping
- Content parsing strategies
- Rate limiting and ethics
- Complex data structures
- Advanced error handling

**Files:**
```text
web-scraper/
├── plugin.py          # Main plugin class
├── config.yaml        # Configuration
├── models.py          # Database models
├── handlers/
│   ├── scraper.py     # Web scraping engine
│   ├── parser.py      # Content parsing
│   ├── analyzer.py    # AI content analysis
│   └── api.py        # REST endpoints
├── templates/         # LLM prompt templates
│   ├── extraction.yaml
│   └── analysis.yaml
└── frontend/
    └── WebScraper.tsx  # React interface
```

## 🎓 Learning Progression

### Start Here: Text Analyzer
1. **Copy the example** - Get familiar with the structure
2. **Modify the prompts** - Change how AI analyzes text
3. **Add new features** - Language detection, keyword extraction
4. **Customize UI** - Add charts, export functionality

### Next: Data Processor
1. **Understand data flow** - File upload → processing → storage
2. **Extend analysis** - Add ML models, statistical tests
3. **Improve visualizations** - More chart types, interactive features
4. **Add real-time updates** - WebSocket progress updates

### Advanced: Web Scraper
1. **Study async patterns** - Concurrent scraping, rate limiting
2. **Enhance parsing** - Multiple content types, better extraction
3. **Add scheduling** - Periodic scraping, monitoring changes
4. **Scale the system** - Distributed scraping, caching

## 🛠️ Customization Guide

### Modify for Your Use Case

1. **Change the Domain**
   ```python
   # Instead of text analysis, make it code analysis
   class CodeAnalyzerPlugin(BasePlugin):
       # Analyze code quality, complexity, patterns
   ```

2. **Add Your Data Sources**
   ```python
   # Instead of CSV files, use APIs, databases, etc.
   async def process_api_data(self, api_endpoint: str):
       # Fetch and analyze API data
   ```

3. **Customize AI Behavior**
   ```yaml
   # config.yaml
   llm:
     model: "gpt-4"  # or claude-3, your custom model
     temperature: 0.3
     system_prompt: "You are a specialized analyst for..."
   ```

### Add New Capabilities

1. **Multiple LLM Providers**
   ```python
   # Use different models for different tasks
   sentiment_response = await llm_manager.generate(messages, model="claude-3")
   summary_response = await llm_manager.generate(messages, model="gpt-4")
   ```

2. **External APIs**
   ```python
   # Integrate with external services
   async def enrich_with_external_data(self, data):
       api_result = await external_api.analyze(data)
       return combined_analysis
   ```

3. **Advanced Database Operations**
   ```python
   # Complex queries, relationships, analytics
   def get_user_analytics(self, user_id: int):
       return db.query().join().filter().group_by().all()
   ```

## 🧪 Testing Examples

Each example includes comprehensive tests:

```bash
# Run tests for an example
cd apps/text-analyzer
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=handlers --cov-report=html
```

### Test Structure
```text
tests/
├── test_plugin.py      # Plugin initialization and config
├── test_processor.py   # Core business logic
├── test_api.py        # API endpoints
└── fixtures/          # Test data and mocks
    ├── sample_text.txt
    └── mock_responses.json
```

## 📚 Next Steps

1. **Pick an example** that matches your skill level
2. **Copy and customize** it for your needs
3. **Build incrementally** - start simple, add features
4. **Share your creation** - contribute back to the community

## 🤝 Contributing Examples

Have a great plugin idea? Contribute an example:

1. **Create a complete example** following the patterns above
2. **Include comprehensive documentation** and tests
3. **Add a tutorial** explaining key concepts
4. **Submit a pull request** with your example

### Example Contribution Template
```text
your-example/
├── README.md           # What it does, how to use it
├── plugin.py          # Complete plugin implementation
├── config.yaml        # Configuration example
├── handlers/          # Business logic
├── tests/             # Unit and integration tests
├── frontend/          # React components (if applicable)
└── docs/              # Tutorial and API docs
```

## 💡 Plugin Ideas

Looking for inspiration? Try building:

- **📧 Email Analyzer** - Analyze email sentiment and urgency
- **🎵 Music Mood Detector** - Analyze song lyrics for mood
- **📊 Survey Processor** - Process survey responses with AI insights
- **🏷️ Auto Tagger** - Automatically tag content using AI
- **📝 Meeting Summarizer** - Summarize meeting transcripts
- **🔍 Document Search** - Semantic search through documents
- **📈 Trend Analyzer** - Analyze trends in time-series data
- **🌍 Translation Helper** - Multi-language content analysis
- **🎯 A/B Test Analyzer** - Analyze experiment results
- **📱 App Review Analyzer** - Analyze app store reviews

---

**Ready to build? Start with the [Text Analyzer](text-analyzer/) example!** 🚀
