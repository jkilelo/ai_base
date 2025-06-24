# Plugin Development Guide - AI Base Platform

This comprehensive guide will walk you through creating powerful AI-powered applications using the AI Base plugin system.

## 🎯 Overview

The AI Base platform uses a plugin architecture that allows you to create extensible, AI-powered applications with minimal boilerplate code. Each plugin is a self-contained application that can leverage:

- **LLM Integration** - Multi-provider AI support (OpenAI, Azure, Anthropic)
- **FastAPI Routing** - Automatic API endpoint registration
- **Database Access** - SQLAlchemy ORM integration
- **Frontend Components** - React.js UI integration
- **Configuration Management** - YAML-based configuration

## 🏗️ Plugin Architecture

```text
Plugin Structure:
├── apps/your_app/
│   ├── plugin.py           # Main plugin class (required)
│   ├── __init__.py         # Python package init
│   ├── config.yaml         # Plugin configuration
│   ├── handlers/           # Business logic modules
│   │   ├── __init__.py
│   │   ├── processor.py    # Core processing logic
│   │   ├── api.py         # Additional API endpoints
│   │   └── models.py      # Database models
│   ├── templates/          # LLM prompt templates
│   │   ├── analysis.yaml
│   │   └── generation.yaml
│   └── tests/             # Unit tests
│       ├── __init__.py
│       ├── test_plugin.py
│       └── test_processor.py
```

## 🚀 Quick Start: Building Your First Plugin

### Step 1: Create Plugin Structure

```bash
# Navigate to the apps directory
cd apps

# Create your plugin directory
mkdir my_analytics_app
cd my_analytics_app

# Create the basic structure
mkdir handlers templates tests
touch __init__.py plugin.py config.yaml
touch handlers/__init__.py handlers/processor.py handlers/api.py handlers/models.py
touch templates/analysis.yaml
touch tests/__init__.py tests/test_plugin.py
```

### Step 2: Define Plugin Configuration

```yaml
# config.yaml
name: "my_analytics_app"
version: "1.0.0"
description: "AI-powered data analytics application"
author: "Your Name"

# Plugin dependencies
dependencies:
  - "pandas>=2.0.0"
  - "numpy>=1.24.0"
  - "plotly>=5.0.0"

# Default configuration
defaults:
  max_data_points: 10000
  analysis_depth: "detailed"
  generate_charts: true
  llm_model: "gpt-4"
  temperature: 0.3

# API endpoints configuration
api:
  prefix: "/analytics"
  tags: ["Analytics"]
  
# Database tables (optional)
database:
  tables:
    - "analytics_jobs"
    - "analytics_results"
```

### Step 3: Create Database Models

```python
# handlers/models.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float
from core.database import Base
import datetime

class AnalyticsJob(Base):
    """Analytics job tracking"""
    __tablename__ = "analytics_jobs"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    input_data = Column(JSON)  # Store input parameters
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)

class AnalyticsResult(Base):
    """Analytics results storage"""
    __tablename__ = "analytics_results"
    
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, nullable=False)  # Foreign key to analytics_jobs
    result_type = Column(String(50))  # insights, charts, statistics
    result_data = Column(JSON)  # Actual results
    confidence_score = Column(Float, nullable=True)
    ai_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
```

### Step 4: Create Core Processor

```python
# handlers/processor.py
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from core.llm import llm_manager, LLMMessage, MessageRole
from .models import AnalyticsJob, AnalyticsResult
from core.database import get_db

class AnalyticsProcessor:
    """Core analytics processing engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_data_points = self.config.get("max_data_points", 10000)
        self.llm_model = self.config.get("llm_model", "gpt-4")
        self.temperature = self.config.get("temperature", 0.3)
    
    async def analyze_dataset(self, data: Dict[str, Any], job_id: int) -> Dict[str, Any]:
        """Perform comprehensive dataset analysis"""
        
        try:
            # Convert data to pandas DataFrame
            df = pd.DataFrame(data.get("records", []))
            
            if len(df) > self.max_data_points:
                df = df.sample(n=self.max_data_points)
            
            # Basic statistical analysis
            stats = self._calculate_statistics(df)
            
            # Generate AI insights
            ai_insights = await self._generate_ai_insights(df, stats)
            
            # Create visualizations (if enabled)
            charts = []
            if self.config.get("generate_charts", True):
                charts = self._generate_charts(df)
            
            result = {
                "statistics": stats,
                "ai_insights": ai_insights,
                "charts": charts,
                "data_quality": self._assess_data_quality(df),
                "row_count": len(df),
                "column_count": len(df.columns)
            }
            
            # Save results to database
            await self._save_results(job_id, result)
            
            return result
            
        except Exception as e:
            await self._update_job_status(job_id, "failed", str(e))
            raise
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive statistics"""
        
        stats = {
            "numeric_columns": {},
            "categorical_columns": {},
            "missing_values": df.isnull().sum().to_dict(),
            "data_types": df.dtypes.astype(str).to_dict()
        }
        
        # Numeric column statistics
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            stats["numeric_columns"][col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "quartiles": df[col].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        
        # Categorical column statistics
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            stats["categorical_columns"][col] = {
                "unique_count": int(df[col].nunique()),
                "top_values": df[col].value_counts().head(5).to_dict(),
                "mode": df[col].mode().iloc[0] if not df[col].mode().empty else None
            }
        
        return stats
    
    async def _generate_ai_insights(self, df: pd.DataFrame, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-powered insights about the dataset"""
        
        # Create a summary for the LLM
        summary = {
            "row_count": len(df),
            "column_count": len(df.columns),
            "column_names": list(df.columns),
            "data_types": stats["data_types"],
            "missing_values": stats["missing_values"],
            "numeric_summary": {col: data["mean"] for col, data in stats["numeric_columns"].items()},
            "categorical_summary": {col: data["unique_count"] for col, data in stats["categorical_columns"].items()}
        }
        
        prompt = f"""
        Analyze this dataset and provide insights:
        
        Dataset Summary:
        {summary}
        
        Please provide:
        1. Key patterns and trends you notice
        2. Data quality observations
        3. Potential business insights
        4. Recommendations for further analysis
        5. Any anomalies or concerns
        
        Format your response as JSON with the following structure:
        {{
            "key_patterns": ["pattern1", "pattern2"],
            "data_quality": {{
                "score": 0.85,
                "issues": ["issue1", "issue2"],
                "strengths": ["strength1", "strength2"]
            }},
            "business_insights": ["insight1", "insight2"],
            "recommendations": ["rec1", "rec2"],
            "anomalies": ["anomaly1", "anomaly2"]
        }}
        """
        
        try:
            response = await llm_manager.generate(
                messages=[LLMMessage(role=MessageRole.USER, content=prompt)],
                model=self.llm_model,
                temperature=self.temperature
            )
            
            # Parse JSON response
            import json
            insights = json.loads(response.content)
            insights["confidence"] = 0.9  # Add confidence score
            
            return insights
            
        except Exception as e:
            return {
                "error": f"Failed to generate AI insights: {str(e)}",
                "confidence": 0.0
            }
    
    def _generate_charts(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate chart configurations for visualization"""
        
        charts = []
        
        # Numeric columns - histograms
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
            charts.append({
                "type": "histogram",
                "title": f"Distribution of {col}",
                "data": {
                    "x": df[col].tolist(),
                    "bins": 20
                },
                "config": {
                    "xaxis_title": col,
                    "yaxis_title": "Frequency"
                }
            })
        
        # Categorical columns - bar charts
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols[:2]:  # Limit to first 2 categorical columns
            value_counts = df[col].value_counts().head(10)
            charts.append({
                "type": "bar",
                "title": f"Top Values in {col}",
                "data": {
                    "x": value_counts.index.tolist(),
                    "y": value_counts.values.tolist()
                },
                "config": {
                    "xaxis_title": col,
                    "yaxis_title": "Count"
                }
            })
        
        return charts
    
    def _assess_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Assess overall data quality"""
        
        total_cells = len(df) * len(df.columns)
        missing_cells = df.isnull().sum().sum()
        completeness = 1 - (missing_cells / total_cells) if total_cells > 0 else 0
        
        # Duplicate row assessment
        duplicate_rows = df.duplicated().sum()
        uniqueness = 1 - (duplicate_rows / len(df)) if len(df) > 0 else 0
        
        # Overall quality score
        quality_score = (completeness + uniqueness) / 2
        
        return {
            "overall_score": round(quality_score, 3),
            "completeness": round(completeness, 3),
            "uniqueness": round(uniqueness, 3),
            "missing_cells": int(missing_cells),
            "duplicate_rows": int(duplicate_rows),
            "assessment": "excellent" if quality_score > 0.9 else 
                         "good" if quality_score > 0.7 else 
                         "fair" if quality_score > 0.5 else "poor"
        }
    
    async def _save_results(self, job_id: int, results: Dict[str, Any]):
        """Save analysis results to database"""
        
        db = next(get_db())
        try:
            # Save main results
            result_record = AnalyticsResult(
                job_id=job_id,
                result_type="complete_analysis",
                result_data=results,
                confidence_score=results.get("ai_insights", {}).get("confidence", 0.0),
                ai_analysis=str(results.get("ai_insights", {}))
            )
            db.add(result_record)
            
            # Update job status
            job = db.query(AnalyticsJob).filter(AnalyticsJob.id == job_id).first()
            if job:
                job.status = "completed"
                job.completed_at = datetime.datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def _update_job_status(self, job_id: int, status: str, error_message: str = None):
        """Update job status in database"""
        
        db = next(get_db())
        try:
            job = db.query(AnalyticsJob).filter(AnalyticsJob.id == job_id).first()
            if job:
                job.status = status
                if error_message:
                    job.error_message = error_message
                if status in ["completed", "failed"]:
                    job.completed_at = datetime.datetime.utcnow()
            db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
```

### Step 5: Create API Endpoints

```python
# handlers/api.py
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from core.database import get_db
from .processor import AnalyticsProcessor
from .models import AnalyticsJob, AnalyticsResult
import datetime

router = APIRouter()

@router.post("/analyze")
async def start_analysis(
    data: Dict[str, Any], 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new analytics job"""
    
    try:
        # Create job record
        job = AnalyticsJob(
            name=data.get("name", f"Analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            status="pending",
            input_data=data
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start background processing
        processor = AnalyticsProcessor(data.get("config", {}))
        background_tasks.add_task(processor.analyze_dataset, data, job.id)
        
        return {
            "success": True,
            "job_id": job.id,
            "message": "Analysis started",
            "status": "pending"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start analysis: {str(e)}")

@router.get("/jobs/{job_id}")
async def get_job_status(job_id: int, db: Session = Depends(get_db)):
    """Get the status of an analytics job"""
    
    job = db.query(AnalyticsJob).filter(AnalyticsJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    result = {
        "job_id": job.id,
        "name": job.name,
        "status": job.status,
        "created_at": job.created_at.isoformat(),
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message
    }
    
    # If completed, include results
    if job.status == "completed":
        results = db.query(AnalyticsResult).filter(AnalyticsResult.job_id == job_id).all()
        result["results"] = [
            {
                "type": r.result_type,
                "data": r.result_data,
                "confidence": r.confidence_score
            }
            for r in results
        ]
    
    return result

@router.get("/jobs")
async def list_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all analytics jobs"""
    
    jobs = db.query(AnalyticsJob).offset(skip).limit(limit).all()
    
    return {
        "jobs": [
            {
                "job_id": job.id,
                "name": job.name,
                "status": job.status,
                "created_at": job.created_at.isoformat()
            }
            for job in jobs
        ],
        "total": len(jobs)
    }

@router.delete("/jobs/{job_id}")
async def delete_job(job_id: int, db: Session = Depends(get_db)):
    """Delete an analytics job and its results"""
    
    # Delete results first
    db.query(AnalyticsResult).filter(AnalyticsResult.job_id == job_id).delete()
    
    # Delete job
    job = db.query(AnalyticsJob).filter(AnalyticsJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    db.delete(job)
    db.commit()
    
    return {"success": True, "message": "Job deleted successfully"}

@router.get("/stats")
async def get_analytics_stats(db: Session = Depends(get_db)):
    """Get overall analytics statistics"""
    
    total_jobs = db.query(AnalyticsJob).count()
    completed_jobs = db.query(AnalyticsJob).filter(AnalyticsJob.status == "completed").count()
    failed_jobs = db.query(AnalyticsJob).filter(AnalyticsJob.status == "failed").count()
    pending_jobs = db.query(AnalyticsJob).filter(AnalyticsJob.status == "pending").count()
    
    return {
        "total_jobs": total_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "pending_jobs": pending_jobs,
        "success_rate": round(completed_jobs / total_jobs * 100, 2) if total_jobs > 0 else 0
    }
```

### Step 6: Create Main Plugin Class

```python
# plugin.py
from typing import Dict, Any
from fastapi import APIRouter
from core.plugins import BasePlugin, PluginMetadata, PluginStatus
from .handlers.api import router as api_router
from .handlers.processor import AnalyticsProcessor
import yaml
import os

class MyAnalyticsPlugin(BasePlugin):
    """AI-powered data analytics plugin"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        
        # Load configuration from config.yaml
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.yaml_config = yaml.safe_load(f)
        else:
            self.yaml_config = {}
        
        # Merge configs (passed config takes precedence)
        self.merged_config = {**self.yaml_config.get("defaults", {}), **(config or {})}
        
        # Setup API router
        self.router = api_router
        
        # Initialize processor
        self.processor = AnalyticsProcessor(self.merged_config)
    
    @property
    def metadata(self) -> PluginMetadata:
        config = self.yaml_config
        return PluginMetadata(
            name=config.get("name", "my_analytics_app"),
            version=config.get("version", "1.0.0"),
            description=config.get("description", "AI-powered data analytics"),
            author=config.get("author", "Unknown"),
            dependencies=config.get("dependencies", []),
            api_version="1.0",
            status=PluginStatus.ACTIVE,
            config_schema={
                "max_data_points": {"type": "integer", "default": 10000},
                "analysis_depth": {"type": "string", "default": "detailed"},
                "generate_charts": {"type": "boolean", "default": True},
                "llm_model": {"type": "string", "default": "gpt-4"},
                "temperature": {"type": "number", "default": 0.3}
            }
        )
    
    async def initialize(self):
        """Initialize the plugin"""
        print(f"🚀 Initializing {self.metadata.name} v{self.metadata.version}")
        
        # Create database tables if they don't exist
        from core.database import engine
        from .handlers.models import Base
        Base.metadata.create_all(bind=engine)
        
        print(f"✅ {self.metadata.name} initialized successfully")
    
    async def cleanup(self):
        """Cleanup plugin resources"""
        print(f"🧹 Cleaning up {self.metadata.name}")
        # Add any cleanup logic here
        print(f"✅ {self.metadata.name} cleaned up successfully")
    
    def get_config(self) -> Dict[str, Any]:
        """Get plugin configuration"""
        return self.merged_config
    
    def update_config(self, new_config: Dict[str, Any]):
        """Update plugin configuration"""
        self.merged_config.update(new_config)
        self.processor = AnalyticsProcessor(self.merged_config)
```

### Step 7: Register Your Plugin

```python
# main.py (add to existing registrations)
from apps.my_analytics_app.plugin import MyAnalyticsPlugin

# Initialize and register the plugin
analytics_plugin = MyAnalyticsPlugin()
await analytics_plugin.initialize()

app.include_router(
    analytics_plugin.router,
    prefix="/api/v1/analytics",
    tags=["Analytics"]
)
```

### Step 8: Create Unit Tests

```python
# tests/test_plugin.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from apps.my_analytics_app.plugin import MyAnalyticsPlugin
from apps.my_analytics_app.handlers.processor import AnalyticsProcessor

@pytest.fixture
def analytics_plugin():
    return MyAnalyticsPlugin()

@pytest.fixture
def sample_data():
    return {
        "records": [
            {"name": "Alice", "age": 30, "salary": 50000},
            {"name": "Bob", "age": 25, "salary": 45000},
            {"name": "Charlie", "age": 35, "salary": 60000},
            {"name": "Diana", "age": 28, "salary": 52000}
        ]
    }

def test_plugin_metadata(analytics_plugin):
    """Test plugin metadata"""
    metadata = analytics_plugin.metadata
    
    assert metadata.name == "my_analytics_app"
    assert metadata.version == "1.0.0"
    assert "pandas" in str(metadata.dependencies)

@pytest.mark.asyncio
async def test_plugin_initialization(analytics_plugin):
    """Test plugin initialization"""
    await analytics_plugin.initialize()
    assert analytics_plugin.processor is not None

def test_statistics_calculation(sample_data):
    """Test basic statistics calculation"""
    processor = AnalyticsProcessor()
    
    import pandas as pd
    df = pd.DataFrame(sample_data["records"])
    stats = processor._calculate_statistics(df)
    
    assert "numeric_columns" in stats
    assert "categorical_columns" in stats
    assert "age" in stats["numeric_columns"]
    assert "name" in stats["categorical_columns"]
    assert stats["numeric_columns"]["age"]["mean"] == 29.5

def test_data_quality_assessment(sample_data):
    """Test data quality assessment"""
    processor = AnalyticsProcessor()
    
    import pandas as pd
    df = pd.DataFrame(sample_data["records"])
    quality = processor._assess_data_quality(df)
    
    assert "overall_score" in quality
    assert "completeness" in quality
    assert quality["overall_score"] >= 0.0
    assert quality["overall_score"] <= 1.0

@pytest.mark.asyncio
async def test_full_analysis_workflow(sample_data):
    """Test complete analysis workflow"""
    processor = AnalyticsProcessor()
    
    # Mock the LLM response
    mock_llm_manager = AsyncMock()
    mock_llm_manager.generate.return_value = MagicMock(
        content='{"key_patterns": ["test"], "data_quality": {"score": 0.9, "issues": [], "strengths": ["complete"]}, "business_insights": ["good data"], "recommendations": ["continue analysis"], "anomalies": []}'
    )
    
    # Mock database operations
    processor._save_results = AsyncMock()
    processor._update_job_status = AsyncMock()
    
    # Run analysis
    result = await processor.analyze_dataset(sample_data, job_id=1)
    
    assert "statistics" in result
    assert "ai_insights" in result
    assert "data_quality" in result
    assert result["row_count"] == 4
    assert result["column_count"] == 3
```

## 🔧 Advanced Features

### LLM Prompt Templates

Create reusable prompt templates for consistent AI interactions:

```yaml
# templates/analysis.yaml
name: "data_analysis"
description: "Comprehensive data analysis prompt"
template: |
  You are a senior data analyst. Analyze the following dataset:
  
  Dataset Information:
  - Rows: {row_count}
  - Columns: {column_count}
  - Column Types: {column_types}
  - Missing Values: {missing_values}
  
  Statistical Summary:
  {statistical_summary}
  
  Please provide:
  1. Key insights and patterns
  2. Data quality assessment (score 0-1)
  3. Business recommendations
  4. Potential data issues
  
  Respond in JSON format:
  {{
    "insights": ["insight1", "insight2"],
    "quality_score": 0.85,
    "recommendations": ["rec1", "rec2"],
    "issues": ["issue1", "issue2"]
  }}

variables:
  - name: "row_count"
    type: "integer"
    description: "Number of rows in dataset"
  - name: "column_count"
    type: "integer"
    description: "Number of columns in dataset"
  - name: "column_types"
    type: "object"
    description: "Data types of each column"
  - name: "missing_values"
    type: "object"
    description: "Missing value counts per column"
  - name: "statistical_summary"
    type: "string"
    description: "Statistical summary of the data"
```

### Configuration Management

Use YAML configuration for flexible plugin behavior:

```yaml
# config.yaml
name: "advanced_analytics"
version: "2.0.0"
description: "Advanced AI-powered analytics with ML capabilities"

# Feature flags
features:
  enable_ml_models: true
  enable_forecasting: true
  enable_clustering: true
  enable_anomaly_detection: true

# LLM Configuration
llm:
  default_model: "gpt-4"
  fallback_model: "gpt-3.5-turbo"
  temperature: 0.3
  max_tokens: 2000
  timeout: 30

# Processing limits
limits:
  max_dataset_size: 1000000
  max_columns: 500
  max_processing_time: 300  # seconds
  concurrent_jobs: 5

# Output configuration
output:
  include_raw_data: false
  include_charts: true
  chart_formats: ["png", "svg", "html"]
  export_formats: ["json", "csv", "excel"]

# Database configuration
database:
  batch_size: 1000
  connection_pool_size: 10
  query_timeout: 30
```

### Error Handling and Logging

Implement comprehensive error handling:

```python
import logging
from typing import Dict, Any, Optional
from core.exceptions import PluginError, LLMError, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsProcessor:
    async def analyze_dataset(self, data: Dict[str, Any], job_id: int) -> Dict[str, Any]:
        """Analyze dataset with comprehensive error handling"""
        
        try:
            logger.info(f"Starting analysis for job {job_id}")
            
            # Validate input data
            self._validate_input(data)
            
            # Process data with error handling
            result = await self._safe_process(data, job_id)
            
            logger.info(f"Analysis completed successfully for job {job_id}")
            return result
            
        except ValidationError as e:
            logger.error(f"Validation error for job {job_id}: {str(e)}")
            await self._handle_error(job_id, "validation_error", str(e))
            raise PluginError(f"Invalid input data: {str(e)}")
            
        except LLMError as e:
            logger.error(f"LLM error for job {job_id}: {str(e)}")
            await self._handle_error(job_id, "llm_error", str(e))
            raise PluginError(f"AI analysis failed: {str(e)}")
            
        except DatabaseError as e:
            logger.error(f"Database error for job {job_id}: {str(e)}")
            await self._handle_error(job_id, "database_error", str(e))
            raise PluginError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error for job {job_id}: {str(e)}")
            await self._handle_error(job_id, "unexpected_error", str(e))
            raise PluginError(f"Analysis failed: {str(e)}")
    
    def _validate_input(self, data: Dict[str, Any]):
        """Validate input data"""
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")
        
        if "records" not in data:
            raise ValidationError("Data must contain 'records' field")
        
        records = data["records"]
        if not isinstance(records, list) or len(records) == 0:
            raise ValidationError("Records must be a non-empty list")
        
        # Check data size limits
        if len(records) > self.config.get("max_dataset_size", 1000000):
            raise ValidationError("Dataset exceeds maximum size limit")
    
    async def _handle_error(self, job_id: int, error_type: str, error_message: str):
        """Handle and log errors"""
        try:
            await self._update_job_status(job_id, "failed", f"{error_type}: {error_message}")
        except Exception as e:
            logger.error(f"Failed to update job status: {str(e)}")

class ValidationError(Exception):
    """Custom validation error"""
    pass
```

## 🎨 Frontend Integration

### React Component for Your Plugin

```typescript
// v1/frontend/src/components/AnalyticsApp.tsx
import React, { useState, useEffect } from 'react';
import { Card, Button, Alert, ProgressBar, Table } from 'react-bootstrap';
import { ApiService } from '../services/api';

interface AnalyticsJob {
  job_id: number;
  name: string;
  status: string;
  created_at: string;
  completed_at?: string;
  results?: any;
}

export const AnalyticsApp: React.FC = () => {
  const [jobs, setJobs] = useState<AnalyticsJob[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysisConfig, setAnalysisConfig] = useState({
    name: '',
    generate_charts: true,
    analysis_depth: 'detailed',
    llm_model: 'gpt-4'
  });

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      const response = await ApiService.get('/api/v1/analytics/jobs');
      setJobs(response.data.jobs);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    try {
      // Parse CSV file
      const text = await selectedFile.text();
      const lines = text.split('\n');
      const headers = lines[0].split(',');
      const records = lines.slice(1).map(line => {
        const values = line.split(',');
        const record: any = {};
        headers.forEach((header, index) => {
          record[header.trim()] = values[index]?.trim();
        });
        return record;
      }).filter(record => Object.keys(record).length > 0);

      // Start analysis
      const response = await ApiService.post('/api/v1/analytics/analyze', {
        name: analysisConfig.name || selectedFile.name,
        records: records,
        config: analysisConfig
      });

      if (response.data.success) {
        await loadJobs();
        setSelectedFile(null);
        setAnalysisConfig({ ...analysisConfig, name: '' });
      }
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderJobStatus = (status: string) => {
    const variant = status === 'completed' ? 'success' : 
                   status === 'failed' ? 'danger' : 
                   status === 'running' ? 'warning' : 'info';
    
    return <Alert variant={variant} className="mb-0 py-1">{status}</Alert>;
  };

  const renderResults = (job: AnalyticsJob) => {
    if (!job.results || job.results.length === 0) return null;

    const result = job.results[0].data;
    
    return (
      <div className="mt-3">
        <h6>Analysis Results</h6>
        
        {/* Data Quality Score */}
        <Card className="mb-3">
          <Card.Body>
            <Card.Title>Data Quality</Card.Title>
            <ProgressBar 
              now={result.data_quality.overall_score * 100} 
              label={`${Math.round(result.data_quality.overall_score * 100)}%`}
              variant={result.data_quality.overall_score > 0.8 ? 'success' : 
                      result.data_quality.overall_score > 0.6 ? 'warning' : 'danger'}
            />
            <small className="text-muted">
              Assessment: {result.data_quality.assessment}
            </small>
          </Card.Body>
        </Card>

        {/* AI Insights */}
        {result.ai_insights && (
          <Card className="mb-3">
            <Card.Body>
              <Card.Title>AI Insights</Card.Title>
              {result.ai_insights.key_patterns && (
                <div>
                  <strong>Key Patterns:</strong>
                  <ul>
                    {result.ai_insights.key_patterns.map((pattern: string, index: number) => (
                      <li key={index}>{pattern}</li>
                    ))}
                  </ul>
                </div>
              )}
              {result.ai_insights.recommendations && (
                <div>
                  <strong>Recommendations:</strong>
                  <ul>
                    {result.ai_insights.recommendations.map((rec: string, index: number) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </Card.Body>
          </Card>
        )}

        {/* Statistics Summary */}
        <Card>
          <Card.Body>
            <Card.Title>Dataset Summary</Card.Title>
            <p><strong>Rows:</strong> {result.row_count}</p>
            <p><strong>Columns:</strong> {result.column_count}</p>
            <p><strong>Missing Values:</strong> {result.statistics.missing_values ? 
              Object.values(result.statistics.missing_values).reduce((a: any, b: any) => a + b, 0) : 0}
            </p>
          </Card.Body>
        </Card>
      </div>
    );
  };

  return (
    <div className="container mt-4">
      <h2>Analytics Dashboard</h2>
      
      {/* Upload Section */}
      <Card className="mb-4">
        <Card.Body>
          <Card.Title>Start New Analysis</Card.Title>
          
          <div className="mb-3">
            <label className="form-label">Upload CSV File</label>
            <input 
              type="file" 
              accept=".csv"
              className="form-control"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            />
          </div>

          <div className="mb-3">
            <label className="form-label">Analysis Name</label>
            <input 
              type="text"
              className="form-control"
              value={analysisConfig.name}
              onChange={(e) => setAnalysisConfig({...analysisConfig, name: e.target.value})}
              placeholder="Enter analysis name"
            />
          </div>

          <div className="mb-3">
            <div className="form-check">
              <input 
                type="checkbox"
                className="form-check-input"
                checked={analysisConfig.generate_charts}
                onChange={(e) => setAnalysisConfig({...analysisConfig, generate_charts: e.target.checked})}
              />
              <label className="form-check-label">Generate Charts</label>
            </div>
          </div>

          <Button 
            variant="primary" 
            onClick={handleFileUpload}
            disabled={!selectedFile || loading}
          >
            {loading ? 'Analyzing...' : 'Start Analysis'}
          </Button>
        </Card.Body>
      </Card>

      {/* Jobs List */}
      <Card>
        <Card.Body>
          <Card.Title>Analysis Jobs</Card.Title>
          
          {jobs.length === 0 ? (
            <p>No analysis jobs found. Start by uploading a CSV file.</p>
          ) : (
            <div>
              {jobs.map((job) => (
                <Card key={job.job_id} className="mb-3">
                  <Card.Body>
                    <div className="d-flex justify-content-between align-items-center">
                      <div>
                        <h6>{job.name}</h6>
                        <small className="text-muted">
                          Created: {new Date(job.created_at).toLocaleString()}
                        </small>
                      </div>
                      {renderJobStatus(job.status)}
                    </div>
                    
                    {job.status === 'completed' && renderResults(job)}
                  </Card.Body>
                </Card>
              ))}
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
};
```

## 📚 Best Practices

### 1. Plugin Structure
- Keep plugins self-contained
- Use clear naming conventions
- Separate concerns (API, business logic, data models)
- Include comprehensive configuration

### 2. Error Handling
- Implement robust error handling at all levels
- Use custom exception types
- Log errors appropriately
- Provide meaningful error messages to users

### 3. Performance
- Implement async/await for I/O operations
- Use background tasks for long-running operations
- Implement proper database connection pooling
- Add caching where appropriate

### 4. Testing
- Write unit tests for all core functionality
- Include integration tests for API endpoints
- Mock external dependencies (LLM calls, databases)
- Test error scenarios

### 5. Documentation
- Document all API endpoints
- Include configuration examples
- Provide usage examples
- Document deployment requirements

## 🚀 Deployment

### Development
```bash
# Start the platform
.\setup.ps1
.\start_backend.ps1

# Your plugin will be automatically loaded
```

### Production
```bash
# Build for production
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Or use Docker
docker build -t ai-base-platform .
docker run -p 8000:8000 ai-base-platform
```

## 🤝 Contributing

1. Follow the plugin structure guidelines
2. Include comprehensive tests
3. Document your plugin thoroughly
4. Submit pull requests with clear descriptions

---

**Ready to build your AI-powered application? Start with the quick start guide above!** 🚀
