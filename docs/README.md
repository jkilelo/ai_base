# AI Base Platform - Documentation

📚 **Comprehensive documentation for building AI-powered applications**

Welcome to the AI Base platform documentation. This directory contains everything you need to build, deploy, and scale AI-powered applications using our extensible plugin framework.

## 🚀 Getting Started

| Guide                                                       | Description                               | Time   |
| ----------------------------------------------------------- | ----------------------------------------- | ------ |
| **[Quick Start Guide](QUICK_START_GUIDE.md)**               | Build your first AI app in 10 minutes     | 10 min |
| **[Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)** | Comprehensive plugin development tutorial | 30 min |
| **[Architecture Overview](../ARCHITECTURE.md)**             | System design and core concepts           | 15 min |

## 📖 Documentation Structure

```text
docs/
├── QUICK_START_GUIDE.md        # 🚀 Build your first app (10 min)
├── PLUGIN_DEVELOPMENT_GUIDE.md # 🏗️ Complete development guide
├── api/                        # 📡 API documentation
│   ├── endpoints.md            # REST API reference
│   ├── authentication.md      # Auth and security
│   └── health-checks.md        # Health monitoring
├── tutorials/                  # 🎓 Step-by-step tutorials
│   ├── getting-started.md      # Platform setup
│   ├── building-apps.md        # App development
│   ├── testing.md             # Testing strategies
│   └── deployment.md          # Production deployment
├── examples/                   # 💡 Example applications
│   ├── text-analyzer/         # Simple text analysis app
│   ├── data-processor/        # Data processing app
│   └── web-scraper/           # Web scraping app
└── README.md                  # This file
```

## 🎯 What You Can Build

The AI Base platform enables rapid development of:

### 📊 Data Analysis Apps
- CSV/Excel data processing
- Statistical analysis with AI insights
- Interactive dashboards
- Automated reporting

### 🌐 Web Applications
- Content analyzers
- Web scrapers
- URL processors
- SEO tools

### 🤖 AI-Powered Tools
- Text generators
- Code analyzers
- Translation services
- Sentiment analysis

### 🔍 Testing & Quality Apps
- Automated UI testing
- Code quality analysis
- Data validation
- Performance monitoring

## 🏗️ Core Concepts

### Plugin Architecture
Every application is a **plugin** with:
- Self-contained functionality
- Automatic API registration
- Database integration
- LLM access
- Frontend components

### LLM Integration
Built-in support for:
- **OpenAI** (GPT-4, GPT-3.5)
- **Azure OpenAI** (Enterprise)
- **Anthropic** (Claude)
- **Custom providers**

### Tech Stack
- **Backend**: Python 3.12+, FastAPI, SQLAlchemy
- **Frontend**: React 19.1, TypeScript, Bootstrap 5.3
- **AI**: Multi-provider LLM support
- **Database**: SQLite, PostgreSQL, MongoDB
- **Tools**: UV package manager, Playwright

## 📚 Learning Path

### 1. Beginner (30 minutes)
1. **[Quick Start Guide](QUICK_START_GUIDE.md)** - Build your first app
2. **[Architecture Overview](../ARCHITECTURE.md)** - Understand the system
3. **Test the built-in apps** - Web Testing & Data Quality

### 2. Intermediate (2 hours)
1. **[Plugin Development Guide](PLUGIN_DEVELOPMENT_GUIDE.md)** - Deep dive
2. **Build a custom app** - Follow the comprehensive tutorial
3. **Add frontend components** - React integration
4. **Deploy locally** - Production setup

### 3. Advanced (Full day)
1. **Custom LLM providers** - Integrate new AI services
2. **Database design** - Custom models and relationships
3. **Performance optimization** - Scaling and caching
4. **Production deployment** - Docker, monitoring, CI/CD

## 🛠️ Development Workflow

### 1. Setup Environment
```bash
# One-time setup
.\setup.ps1

# Start development
.\start_backend.ps1    # Terminal 1
cd v1\frontend && npm start  # Terminal 2
```

### 2. Create Your Plugin
```bash
# Create app structure
mkdir apps\my_app
cd apps\my_app

# Implement plugin (see guides)
# - plugin.py (main class)
# - handlers/ (business logic)
# - config.yaml (configuration)
```

### 3. Test and Deploy
```bash
# Run tests
pytest apps\my_app\tests\

# Production build
npm run build          # Frontend
uvicorn main:app       # Backend
```

## 📡 API Reference

### Core Endpoints
- `GET /health` - System health check
- `GET /api/v1/plugins` - List available plugins
- `POST /api/v1/{plugin}/action` - Plugin-specific actions

### Built-in Apps
- **Web Testing**: `/api/v1/web-testing/*`
- **Data Quality**: `/api/v1/data-quality/*`
- **Your Apps**: `/api/v1/{your-app}/*`

### Authentication
- API key authentication
- Rate limiting
- CORS support

## 🧪 Example Applications

### Text Analyzer (Beginner)
```python
# Simple text analysis with AI insights
@router.post("/analyze")
async def analyze_text(text: str):
    result = await llm_manager.generate(f"Analyze: {text}")
    return {"analysis": result.content}
```

### Data Processor (Intermediate)
```python
# CSV processing with AI-powered insights
@router.post("/process")
async def process_data(file: UploadFile):
    df = pd.read_csv(file.file)
    insights = await generate_ai_insights(df)
    return {"data": df.to_dict(), "insights": insights}
```

### Web Scraper (Advanced)
```python
# Intelligent web scraping with content analysis
@router.post("/scrape")
async def scrape_url(url: str):
    content = await crawler.scrape(url)
    analysis = await llm_manager.analyze_content(content)
    return {"content": content, "analysis": analysis}
```

## 🚀 Deployment

### Development
```bash
# Local development (auto-reload)
.\start_backend.ps1
cd v1\frontend && npm start
```

### Production
```bash
# Build optimized frontend
cd v1\frontend && npm run build

# Start production backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker
```dockerfile
# Multi-stage build for production
FROM node:18 AS frontend
# ... frontend build

FROM python:3.12 AS backend
# ... backend setup
```

## 🤝 Contributing

### Plugin Submission
1. Follow the plugin development guide
2. Include comprehensive tests
3. Add documentation and examples
4. Submit pull request

### Core Platform
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

## 📋 Troubleshooting

### Common Issues

**Python Version Error**
```bash
# Fix: Use Python 3.12+
py -3.12 --version
.\check_python.py
```

**Dependencies Not Installing**
```bash
# Fix: Clean and reinstall
.\setup.ps1 --clean
```

**LLM API Errors**
```bash
# Fix: Check API keys in .env
cp .env.template .env
# Edit .env with your API keys
```

### Getting Help

1. **Check the guides** - Most issues are covered
2. **Review examples** - See working implementations
3. **Test built-in apps** - Verify your setup
4. **Check logs** - Backend and frontend console output

## 📄 License

This documentation is part of the AI Base Platform, licensed under the MIT License.

---

**Ready to build AI-powered applications? Start with the [Quick Start Guide](QUICK_START_GUIDE.md)!** 🚀
- Database health verification
- Dependency status tracking
- Performance metrics collection

### 🛠️ Development
- Setting up development environment
- Code structure and organization
- Testing strategies
- Debug and troubleshooting

### 🚀 Deployment
- Production deployment guide
- Environment configuration
- Docker containerization
- CI/CD pipeline setup

## Health Check System Documentation

The AI Base Project includes a comprehensive health check system that monitors:

### System Health
- **CPU Usage**: Monitor processor utilization
- **Memory Usage**: Track RAM consumption and availability
- **Disk Space**: Monitor storage usage and availability
- **Load Average**: System load monitoring (Unix systems)

### Database Health
- **Connection Status**: Verify database connectivity
- **Query Performance**: Test basic database operations
- **File Size**: Monitor database file growth (SQLite)
- **Connection Pool**: Monitor connection pool status

### Dependencies Health
- **Critical Dependencies**: FastAPI, Uvicorn, SQLAlchemy, Pydantic
- **Optional Dependencies**: Redis, MongoDB drivers, PostgreSQL drivers
- **Version Tracking**: Monitor dependency versions
- **Security Updates**: Track outdated packages

### Environment Health
- **Python Version**: Verify Python 3.12+ requirement
- **Node.js Availability**: Check frontend development tools
- **Environment Variables**: Validate required configuration
- **File System**: Verify critical directories and files

## Health Check Endpoints

### Basic Health Check
```http
GET /api/v1/health
```

Returns simple status for load balancer health checks.

### Detailed Health Check
```http
GET /api/v1/health/detailed
```

Comprehensive system status with all components.

### Database Health Check
```http
GET /api/v1/health/database
```

Database-specific connectivity and performance tests.

### System Health Check
```http
GET /api/v1/health/system
```

System resource usage and availability.

### Dependencies Health Check
```http
GET /api/v1/health/dependencies
```

Verify all required and optional dependencies.

## Health Status Levels

| Status      | Description                      | HTTP Code |
| ----------- | -------------------------------- | --------- |
| `healthy`   | All systems operational          | 200       |
| `degraded`  | Minor issues, service functional | 200       |
| `warning`   | Potential issues detected        | 200       |
| `critical`  | Major issues, service impacted   | 503       |
| `unhealthy` | Service unavailable              | 503       |

## Monitoring Integration

The health check system is designed to integrate with:

- **Load Balancers**: Basic health endpoint for traffic routing
- **Monitoring Tools**: Prometheus, Grafana, DataDog
- **Alerting Systems**: PagerDuty, Slack notifications
- **Logging Platforms**: ELK Stack, Splunk
- **APM Tools**: New Relic, AppDynamics

## Usage Examples

### Development Monitoring
```bash
# Quick health check
curl http://localhost:8000/api/v1/health

# Detailed status
curl http://localhost:8000/api/v1/health/detailed

# Database status
curl http://localhost:8000/api/v1/health/database
```

### Production Monitoring
```bash
# Load balancer health check
wget --quiet --spider http://api.example.com/api/v1/health

# Monitoring script
#!/bin/bash
STATUS=$(curl -s http://api.example.com/api/v1/health | jq -r '.status')
if [ "$STATUS" != "healthy" ]; then
    echo "API unhealthy: $STATUS"
    # Send alert
fi
```

## Tech Stack Requirements

### Backend
- **Python 3.12+**: Core runtime environment
- **FastAPI**: Web framework for API development
- **Uvicorn**: ASGI server for production deployment
- **SQLAlchemy**: Database ORM for data management
- **Pydantic**: Data validation and settings management
- **psutil**: System monitoring and resource tracking

### Frontend
- **Node.js 22.16+ LTS**: JavaScript runtime
- **React 19.1**: User interface framework
- **TypeScript**: Type-safe JavaScript development
- **Bootstrap 5.3**: UI component library

### Database
- **SQLite**: Default development database
- **PostgreSQL 17**: Production database option
- **MongoDB**: NoSQL database option

### Development Tools
- **CRACO**: Create React App configuration override
- **Webpack**: Module bundler with hot reloading
- **ESLint**: Code linting and quality
- **Prettier**: Code formatting

## Getting Started

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd ai_base
   ```

2. **Setup Environment**
   ```bash
   # Complete setup
   setup-environment.bat
   
   # Or manual setup
   copy .env.template .env
   # Edit .env with your configuration
   ```

3. **Start Backend**
   ```bash
   cd v1/backend
   python -m uvicorn app.main:app --reload
   ```

4. **Start Frontend**
   ```bash
   cd v1/frontend
   npm start
   ```

5. **Verify Health**
   ```bash
   curl http://localhost:8000/api/v1/health/detailed
   ```

## Contributing

When adding new features or making changes:

1. Update relevant documentation
2. Add health checks for new components
3. Include monitoring and alerting considerations
4. Test health check endpoints
5. Update API documentation

## Support and Troubleshooting

For issues and support:

1. Check health check endpoints for system status
2. Review application logs for error details
3. Verify environment configuration
4. Check dependency versions and compatibility
5. Consult troubleshooting guide in `tutorials/troubleshooting.md`

This documentation is automatically updated as the system evolves to ensure accuracy and completeness.
