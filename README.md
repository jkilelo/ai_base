# AI Base Platform - Extensible AI-Powered Development Framework

🚀 **Build AI-powered applications rapidly with our extensible plugin-based platform**

AI Base is a highly extensible, plugin-based platform designed for rapid development of LLM-driven applications. Create sophisticated AI tools for web testing, data quality, automation, and more with minimal boilerplate code.

## 🎯 What You Can Build

- **🌐 Web UI Testing Apps** - AI-powered test generation with Playwright
- **📊 Data Quality Apps** - Intelligent data profiling and validation
- **🤖 Automation Tools** - LLM-driven workflow automation
- **🔍 Analysis Platforms** - Data analysis and reporting tools
- **🎨 Custom AI Applications** - Any LLM-powered solution you can imagine

## 🛠️ Tech Stack

| Frontend          | Backend          | AI/LLM           | Database       | Tools                  |
| ----------------- | ---------------- | ---------------- | -------------- | ---------------------- |
| **React 19.1**    | **Python 3.12+** | **OpenAI API**   | **SQLite3**    | **UV Package Manager** |
| **Bootstrap 5.3** | **FastAPI**      | **Azure OpenAI** | **PostgreSQL** | **TypeScript**         |
| **TypeScript**    | **SQLAlchemy**   | **Anthropic**    | **MongoDB**    | **Playwright**         |

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** (Required - enforced by setup scripts)
- **Node.js 18+** (for React frontend)
- **Git** (for version control)

### 1. Setup Environment

Choose your setup method:

```powershell
# PowerShell (Recommended)
.\setup.ps1

# Or Batch
setup.bat
```

The setup script will:

- ✅ Verify Python 3.12+ installation
- ✅ Install UV package manager
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Setup frontend with React 19.1

### 2. Start Development

```powershell
# Start backend API
.\start_backend.ps1

# Start frontend (new terminal)
cd v1\frontend
npm start
```

### 3. Access Your Platform

| Service         | URL                          | Description                   |
| --------------- | ---------------------------- | ----------------------------- |
| **Frontend**    | <http://localhost:3000>      | React.js application          |
| **Backend API** | <http://localhost:8000>      | FastAPI application           |
| **API Docs**    | <http://localhost:8000/docs> | Interactive API documentation |

## 📱 Building Your First App

### Step 1: Create Your Plugin

Create a new directory in the `apps/` folder:

```text
apps/
└── your_app_name/
    ├── plugin.py          # Main plugin implementation
    ├── __init__.py        # Python package init
    ├── config.yaml        # App configuration
    └── handlers/           # Business logic modules
        ├── __init__.py
        ├── processor.py    # Core processing logic
        └── api.py         # API endpoints
```

### Step 2: Implement Your Plugin

```python
# apps/your_app_name/plugin.py
from typing import Dict, Any
from fastapi import APIRouter
from core.plugins import BasePlugin, PluginMetadata
from core.llm import llm_manager

class YourAppPlugin(BasePlugin):
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.router = APIRouter()
        self._setup_routes()

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="your_app_name",
            version="1.0.0",
            description="Your app description",
            author="Your Name",
            dependencies=["requests", "pandas"],  # Add your deps
            api_version="1.0"
        )

    def _setup_routes(self):
        @self.router.post("/process")
        async def process_data(data: dict):
            # Use LLM for processing
            response = await llm_manager.generate(
                messages=[{
                    "role": "user", 
                    "content": f"Process this data: {data}"
                }]
            )
            return {"result": response.content}

    async def initialize(self):
        """Initialize your app"""
        print(f"Initializing {self.metadata.name}")

    async def cleanup(self):
        """Cleanup resources"""
        print(f"Cleaning up {self.metadata.name}")
```

### Step 3: Register Your Plugin

Add your plugin to the main application:

```python
# main.py (add to existing file)
from apps.your_app_name.plugin import YourAppPlugin

# Register your plugin
app.include_router(
    YourAppPlugin().router, 
    prefix="/api/v1/your_app_name",
    tags=["Your App"]
)
```

### Step 4: Configure LLM Integration

Your app automatically has access to the LLM manager:

```python
from core.llm import llm_manager, LLMMessage, MessageRole

# Simple text generation
response = await llm_manager.generate(
    messages=[
        LLMMessage(role=MessageRole.USER, content="Your prompt here")
    ],
    model="gpt-4",  # Optional: specify model
    temperature=0.7  # Optional: control creativity
)

# Structured output with JSON
response = await llm_manager.generate_json(
    messages=[LLMMessage(role=MessageRole.USER, content="Generate JSON data")],
    schema={
        "type": "object",
        "properties": {
            "result": {"type": "string"},
            "confidence": {"type": "number"}
        }
    }
)
```

## 🏗️ Architecture Overview

### Plugin System

```text
AI Base Platform
├── Core Framework
│   ├── Plugin Manager       # Loads and manages plugins
│   ├── LLM Abstraction     # Multi-provider LLM support
│   ├── API Gateway         # FastAPI routing
│   └── Database Layer      # SQLAlchemy ORM
├── Built-in Apps
│   ├── Web Testing         # Playwright + AI test generation
│   └── Data Quality        # PySpark + AI profiling
└── Your Custom Apps
    └── [Your Plugin]       # Your AI-powered application
```

### Key Components

1. **Plugin Manager** (`core/plugins.py`)
   - Automatic plugin discovery
   - Lifecycle management
   - Dependency injection

2. **LLM Manager** (`core/llm.py`)
   - Multi-provider support (OpenAI, Azure, Anthropic)
   - Token usage tracking
   - Response caching

3. **Database Layer** (`core/database.py`)
   - SQLAlchemy integration
   - Multiple database support
   - Migration management

## 📖 Example Applications

### Web Testing App

Automatically generates Playwright tests from URLs:

```python
# Example usage
crawler = AdvancedWebCrawler()
pages = await crawler.crawl_website("https://example.com", max_depth=2)

generator = LLMTestGenerator()
tests = await generator.generate_tests(pages, framework=TestFramework.PLAYWRIGHT)
```

### Data Quality App

AI-powered data profiling and validation:

```python
# Example usage
profiler = DataProfiler()
profile = await profiler.analyze_dataset("data.csv")

generator = SparkCodeGenerator()
validation_code = await generator.generate_dq_rules(profile)
```

## 🔧 Advanced Features

### Custom LLM Providers

Add support for new LLM providers:

```python
from core.llm import BaseLLMProvider

class CustomLLMProvider(BaseLLMProvider):
    async def generate(self, messages, **kwargs):
        # Implement your custom LLM logic
        pass
```

### Database Models

Create custom database models:

```python
from sqlalchemy import Column, Integer, String
from core.database import Base

class YourModel(Base):
    __tablename__ = "your_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
```

### Frontend Integration

Add React components for your app:

```typescript
// v1/frontend/src/components/YourApp.tsx
import React from 'react';
import { ApiService } from '../services/api';

export const YourAppComponent: React.FC = () => {
  const handleProcess = async (data: any) => {
    const result = await ApiService.post('/api/v1/your_app_name/process', data);
    return result;
  };

  return (
    <div className="container">
      {/* Your React UI here */}
    </div>
  );
};
```

## 📁 Project Structure

```text
ai_base/
├── setup.ps1              # PowerShell setup script
├── setup.bat              # Batch setup script  
├── check_python.py        # Python version checker
├── main.py                # Main FastAPI application
├── pyproject.toml         # Python project configuration
├── core/                  # Core framework
│   ├── plugins.py         # Plugin system
│   ├── llm.py            # LLM abstraction
│   └── database.py       # Database layer
├── apps/                  # Plugin applications
│   ├── web_testing/       # Web UI testing plugin
│   │   ├── plugin.py      # Main plugin
│   │   ├── crawler.py     # Web crawler
│   │   └── test_generator.py # Test generation
│   └── data_quality/      # Data quality plugin
│       ├── plugin.py      # Main plugin
│       ├── profiler.py    # Data profiler
│       └── spark_generator.py # PySpark code gen
├── v1/                    # Frontend application
│   └── frontend/          # React 19.1 UI
│       ├── src/
│       ├── package.json
│       └── public/
└── docs/                  # Documentation
    ├── README.md
    └── tutorials/
```

## 🎓 Plugin Development Tutorial

### 1. Planning Your Plugin

Before coding, define:

- **Purpose**: What problem does your app solve?
- **Inputs**: What data does it need?
- **Outputs**: What does it produce?
- **LLM Usage**: How will AI enhance the functionality?

### 2. Create Plugin Structure

```bash
# Create your app directory
mkdir apps/my_app
cd apps/my_app

# Create required files
touch __init__.py plugin.py config.yaml
mkdir handlers
cd handlers
touch __init__.py processor.py api.py
```

### 3. Implement Core Logic

```python
# apps/my_app/handlers/processor.py
from typing import Dict, Any
from core.llm import llm_manager

class MyAppProcessor:
    def __init__(self):
        self.name = "My App Processor"
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing logic"""
        
        # Use LLM for intelligent processing
        prompt = f"Analyze this data and provide insights: {input_data}"
        
        response = await llm_manager.generate(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4",
            temperature=0.3
        )
        
        return {
            "input": input_data,
            "ai_analysis": response.content,
            "processed_at": "2025-06-24T12:00:00Z"
        }
```

### 4. Create API Endpoints

```python
# apps/my_app/handlers/api.py
from fastapi import APIRouter, HTTPException
from .processor import MyAppProcessor

router = APIRouter()
processor = MyAppProcessor()

@router.post("/analyze")
async def analyze_data(data: dict):
    """Analyze data using AI"""
    try:
        result = await processor.process(data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """Get app status"""
    return {"status": "active", "app": "my_app"}
```

### 5. Wire Everything Together

```python
# apps/my_app/plugin.py
from core.plugins import BasePlugin, PluginMetadata
from .handlers.api import router

class MyAppPlugin(BasePlugin):
    def __init__(self, config=None):
        super().__init__(config)
        self.router = router
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my_app",
            version="1.0.0",
            description="My custom AI-powered application",
            author="Your Name",
            dependencies=["requests"],
            api_version="1.0"
        )
    
    async def initialize(self):
        print("My App initialized successfully!")
    
    async def cleanup(self):
        print("My App cleaned up!")
```

### 6. Register and Test

```python
# main.py (add your plugin)
from apps.my_app.plugin import MyAppPlugin

# Register the plugin
my_app = MyAppPlugin()
app.include_router(my_app.router, prefix="/api/v1/my_app", tags=["My App"])
```

Test your endpoints:

- `GET http://localhost:8000/api/v1/my_app/status`
- `POST http://localhost:8000/api/v1/my_app/analyze`

## 🧪 Testing Your Plugin

### Unit Tests

```python
# tests/test_my_app.py
import pytest
from apps.my_app.handlers.processor import MyAppProcessor

@pytest.mark.asyncio
async def test_processor():
    processor = MyAppProcessor()
    result = await processor.process({"test": "data"})
    
    assert "ai_analysis" in result
    assert result["input"]["test"] == "data"
```

### Integration Tests

```python
# tests/test_my_app_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_status_endpoint():
    response = client.get("/api/v1/my_app/status")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

def test_analyze_endpoint():
    response = client.post(
        "/api/v1/my_app/analyze",
        json={"sample": "data"}
    )
    assert response.status_code == 200
    assert "data" in response.json()
```

## 📚 Advanced Tutorials

### Working with Large Language Models

```python
# Advanced LLM usage patterns
from core.llm import llm_manager, PromptTemplate

# Create reusable prompt templates
analysis_template = PromptTemplate(
    name="data_analysis",
    template="""
    Analyze the following data and provide:
    1. Key insights
    2. Potential issues
    3. Recommendations
    
    Data: {data}
    
    Format the response as JSON with the following structure:
    {{
        "insights": ["insight1", "insight2"],
        "issues": ["issue1", "issue2"],
        "recommendations": ["rec1", "rec2"]
    }}
    """
)

# Use the template
response = await llm_manager.generate_with_template(
    template=analysis_template,
    variables={"data": your_data},
    model="gpt-4"
)
```

### Database Integration

```python
# Create custom database models
from sqlalchemy import Column, Integer, String, DateTime, Text
from core.database import Base
import datetime

class MyAppData(Base):
    __tablename__ = "my_app_data"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    analysis_result = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Use in your plugin
from core.database import get_db

async def save_analysis(name: str, result: str):
    db = next(get_db())
    data = MyAppData(name=name, analysis_result=result)
    db.add(data)
    db.commit()
    return data.id
```

## 🚀 Deployment

### Development Mode

```bash
# Backend
.\start_backend.ps1

# Frontend  
cd v1\frontend
npm start
```

### Production Mode

```bash
# Build frontend
cd v1\frontend
npm run build

# Start backend in production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 Documentation

- 📖 [Architecture Guide](ARCHITECTURE.md) - Detailed system architecture
- 🔧 [API Reference](docs/) - Complete API documentation
- 🎯 [Plugin Development](docs/tutorials/) - Step-by-step plugin creation
- 🚀 [Deployment Guide](docs/deployment/) - Production deployment

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to build something amazing? Start with `.\setup.ps1` and create your first AI-powered app!** 🚀
