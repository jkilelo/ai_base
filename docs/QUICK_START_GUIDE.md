# Quick Start Guide - Building Apps with AI Base

🚀 **Get started building AI-powered applications in 10 minutes**

This guide will walk you through creating your first AI-powered application using the AI Base platform.

## ⚡ Setup (2 minutes)

### 1. Clone and Setup Environment

```powershell
# Clone the repository
git clone <your-repo-url> ai_base
cd ai_base

# Setup environment (auto-installs Python 3.12+, UV, dependencies)
.\setup.ps1
```

### 2. Start the Platform

```powershell
# Terminal 1: Start backend
.\start_backend.ps1

# Terminal 2: Start frontend
cd v1\frontend
npm start
```

### 3. Verify Installation

Open your browser:

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000/docs>

## 🎯 Build Your First App (5 minutes)

Let's create a simple "Text Analyzer" app that uses AI to analyze text.

### Step 1: Create App Structure

```powershell
# Create your app directory
mkdir apps\text_analyzer
cd apps\text_analyzer

# Create required files
New-Item -ItemType File -Name "__init__.py", "plugin.py", "config.yaml"
mkdir handlers
cd handlers
New-Item -ItemType File -Name "__init__.py", "processor.py", "api.py"
cd ..
```

### Step 2: Configure Your App

```yaml
# config.yaml
name: "text_analyzer"
version: "1.0.0"
description: "AI-powered text analysis application"
author: "Your Name"

dependencies:
  - "textstat>=0.7.0"

defaults:
  llm_model: "gpt-4"
  temperature: 0.3
  max_text_length: 5000
```

### Step 3: Create the Processor

```python
# handlers/processor.py
from typing import Dict, Any
from core.llm import llm_manager, LLMMessage, MessageRole
import textstat

class TextProcessor:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.llm_model = self.config.get("llm_model", "gpt-4")
        self.temperature = self.config.get("temperature", 0.3)
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using AI and statistics"""
        
        # Basic text statistics
        stats = {
            "word_count": len(text.split()),
            "character_count": len(text),
            "sentence_count": textstat.sentence_count(text),
            "reading_time_minutes": round(len(text.split()) / 200, 1),  # 200 WPM average
            "readability_score": textstat.flesch_reading_ease(text)
        }
        
        # AI-powered analysis
        prompt = f"""
        Analyze this text and provide insights:
        
        Text: "{text[:1000]}{'...' if len(text) > 1000 else ''}"
        
        Provide analysis in JSON format:
        {{
            "sentiment": "positive/negative/neutral",
            "tone": "formal/informal/conversational/technical",
            "key_themes": ["theme1", "theme2"],
            "summary": "brief summary",
            "writing_style": "description of writing style",
            "target_audience": "likely target audience"
        }}
        """
        
        try:
            response = await llm_manager.generate(
                messages=[LLMMessage(role=MessageRole.USER, content=prompt)],
                model=self.llm_model,
                temperature=self.temperature
            )
            
            import json
            ai_analysis = json.loads(response.content)
            
        except Exception as e:
            ai_analysis = {"error": f"AI analysis failed: {str(e)}"}
        
        return {
            "statistics": stats,
            "ai_analysis": ai_analysis,
            "processed_at": "2025-06-24T12:00:00Z"
        }
```

### Step 4: Create API Endpoints

```python
# handlers/api.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .processor import TextProcessor

router = APIRouter()
processor = TextProcessor()

class TextAnalysisRequest(BaseModel):
    text: str
    options: dict = {}

@router.post("/analyze")
async def analyze_text(request: TextAnalysisRequest):
    """Analyze text using AI"""
    
    if len(request.text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        result = await processor.analyze_text(request.text)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "text_analyzer"}
```

### Step 5: Create the Main Plugin

```python
# plugin.py
from typing import Dict, Any
from core.plugins import BasePlugin, PluginMetadata, PluginStatus
from .handlers.api import router
import yaml
import os

class TextAnalyzerPlugin(BasePlugin):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Load config
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.yaml_config = yaml.safe_load(f)
        else:
            self.yaml_config = {}
        
        self.router = router
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="text_analyzer",
            version="1.0.0",
            description="AI-powered text analysis",
            author="Your Name",
            dependencies=["textstat>=0.7.0"],
            api_version="1.0",
            status=PluginStatus.ACTIVE
        )
    
    async def initialize(self):
        print("🚀 Text Analyzer plugin initialized!")
    
    async def cleanup(self):
        print("🧹 Text Analyzer plugin cleaned up!")
```

### Step 6: Register Your Plugin

```python
# main.py (add this to the existing file)
from apps.text_analyzer.plugin import TextAnalyzerPlugin

# Initialize and register
text_analyzer = TextAnalyzerPlugin()
await text_analyzer.initialize()

app.include_router(
    text_analyzer.router,
    prefix="/api/v1/text-analyzer",
    tags=["Text Analyzer"]
)
```

## 🧪 Test Your App (2 minutes)

### 1. Restart Backend

```powershell
# Stop current backend (Ctrl+C) and restart
.\start_backend.ps1
```

### 2. Test the API

Open <http://localhost:8000/docs> and find your "Text Analyzer" section.

Test with this payload:

```json
{
  "text": "The quick brown fox jumps over the lazy dog. This is a sample text for analysis.",
  "options": {}
}
```

### 3. Expected Response

```json
{
  "success": true,
  "data": {
    "statistics": {
      "word_count": 16,
      "character_count": 86,
      "sentence_count": 2,
      "reading_time_minutes": 0.1,
      "readability_score": 65.8
    },
    "ai_analysis": {
      "sentiment": "neutral",
      "tone": "informal",
      "key_themes": ["animals", "movement"],
      "summary": "A simple sentence about animals",
      "writing_style": "clear and straightforward",
      "target_audience": "general"
    }
  }
}
```

## 🎨 Add Frontend UI (3 minutes)

### Create React Component

```typescript
// v1/frontend/src/components/TextAnalyzer.tsx
import React, { useState } from 'react';
import { Card, Button, Form, Alert } from 'react-bootstrap';

export const TextAnalyzer: React.FC = () => {
  const [text, setText] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const analyzeText = async () => {
    if (!text.trim()) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/v1/text-analyzer/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, options: {} })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setResult(data.data);
      } else {
        setError('Analysis failed');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-4">
      <h2>🔍 Text Analyzer</h2>
      
      <Card className="mb-4">
        <Card.Body>
          <Form.Group className="mb-3">
            <Form.Label>Enter text to analyze:</Form.Label>
            <Form.Control
              as="textarea"
              rows={4}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter your text here..."
              maxLength={5000}
            />
            <Form.Text className="text-muted">
              {text.length}/5000 characters
            </Form.Text>
          </Form.Group>
          
          <Button 
            variant="primary" 
            onClick={analyzeText}
            disabled={!text.trim() || loading}
          >
            {loading ? 'Analyzing...' : 'Analyze Text'}
          </Button>
        </Card.Body>
      </Card>

      {error && <Alert variant="danger">{error}</Alert>}

      {result && (
        <div>
          <Card className="mb-3">
            <Card.Header><strong>📊 Statistics</strong></Card.Header>
            <Card.Body>
              <p><strong>Words:</strong> {result.statistics.word_count}</p>
              <p><strong>Characters:</strong> {result.statistics.character_count}</p>
              <p><strong>Sentences:</strong> {result.statistics.sentence_count}</p>
              <p><strong>Reading Time:</strong> {result.statistics.reading_time_minutes} min</p>
              <p><strong>Readability Score:</strong> {result.statistics.readability_score}</p>
            </Card.Body>
          </Card>

          <Card>
            <Card.Header><strong>🤖 AI Analysis</strong></Card.Header>
            <Card.Body>
              <p><strong>Sentiment:</strong> {result.ai_analysis.sentiment}</p>
              <p><strong>Tone:</strong> {result.ai_analysis.tone}</p>
              <p><strong>Writing Style:</strong> {result.ai_analysis.writing_style}</p>
              <p><strong>Target Audience:</strong> {result.ai_analysis.target_audience}</p>
              <p><strong>Summary:</strong> {result.ai_analysis.summary}</p>
              {result.ai_analysis.key_themes && (
                <p><strong>Key Themes:</strong> {result.ai_analysis.key_themes.join(', ')}</p>
              )}
            </Card.Body>
          </Card>
        </div>
      )}
    </div>
  );
};
```

### Add to Main App

```typescript
// v1/frontend/src/App.tsx (add to existing routes)
import { TextAnalyzer } from './components/TextAnalyzer';

// Add to your routing:
<Route path="/text-analyzer" element={<TextAnalyzer />} />
```

## 🎉 Congratulations!

You've built your first AI-powered application! Your text analyzer can:

- ✅ Process text with statistical analysis
- ✅ Use AI for sentiment and style analysis
- ✅ Provide a clean React UI
- ✅ Handle errors gracefully
- ✅ Scale automatically with the platform

## 🚀 Next Steps

### Enhance Your App

1. **Add Authentication**
   - User-specific analysis history
   - API rate limiting

2. **Add Database Storage**
   - Save analysis results
   - Track usage analytics

3. **Expand AI Features**
   - Multiple language support
   - Custom analysis types
   - Batch processing

4. **Improve UI**
   - Charts and visualizations
   - Export functionality
   - Real-time analysis

### Build More Apps

Try these ideas:

- **📊 Data Visualizer** - Upload CSV and generate charts
- **🔍 Code Analyzer** - Analyze code quality and style
- **📝 Content Generator** - AI-powered content creation
- **🌐 Web Scraper** - Extract and analyze web content
- **📱 Social Media Analyzer** - Analyze social media posts

### Learn More

- 📖 [Full Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)
- 🏗️ [Architecture Overview](../ARCHITECTURE.md)
- 🔧 [API Reference](../README.md)
- 🧪 [Testing Guide](../tests/)

## 💡 Pro Tips

1. **Start Simple** - Build basic functionality first, then enhance
2. **Use TypeScript** - Better error checking and autocomplete
3. **Test Early** - Write tests as you build features
4. **Monitor Performance** - Use async/await for all I/O operations
5. **Handle Errors** - Always provide meaningful error messages

---

**Ready to build something amazing? The AI Base platform is your foundation for rapid AI app development!** 🚀
