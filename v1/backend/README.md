# AI Base Project v1 - FastAPI Backend

A comprehensive FastAPI backend with an advanced health check system that monitors all aspects of your application including Python environment, Node.js availability, database connectivity, system resources, and dependencies.

## 🚀 Quick Start

### Prerequisites
- ✅ **Python 3.12+** (recommended)
- ✅ **Node.js 22.16+ LTS** (for frontend integration)
- ✅ **Git** (for version control)

### Option 1: Automated Setup (Windows)
```bash
# Start the backend server with automatic dependency installation
start_backend.bat
```

### Option 2: Manual Setup
```bash
# 1. Navigate to backend directory
cd v1/backend

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start development server
python -m uvicorn app.main:app --reload --host localhost --port 8000
```

### Option 3: Python Script
```bash
# Start with the development server script
python start_dev_server.py
```

## 📊 Health Check System

This backend includes a **comprehensive health check system** that ensures your application is healthy by monitoring:

### 🔍 System Health Monitoring
- **CPU Usage**: Real-time processor utilization
- **Memory Usage**: RAM consumption and availability  
- **Disk Space**: Storage usage and free space
- **Load Average**: System load monitoring (Unix systems)

### 🗄️ Database Health Verification
- **Connection Status**: Database connectivity tests
- **Query Performance**: Basic database operation testing
- **File Size Monitoring**: SQLite database file growth tracking
- **Connection Pool**: Connection pool status monitoring

### 📦 Dependencies Health Tracking
- **Critical Dependencies**: FastAPI, Uvicorn, SQLAlchemy, Pydantic
- **Optional Dependencies**: Redis, MongoDB drivers, PostgreSQL drivers
- **Version Tracking**: Monitor dependency versions for security
- **Installation Status**: Verify all required packages are available

### 🌍 Environment Health Validation
- **Python Version**: Verify Python 3.12+ requirement
- **Node.js Availability**: Check frontend development tools
- **Environment Variables**: Validate required configuration
- **File System**: Verify critical directories and files exist

## 🛠️ Health Check Endpoints

### Basic Health Check
```http
GET http://localhost:8000/api/v1/health
```
**Purpose**: Simple health status for load balancers and quick checks
```json
{
  "status": "healthy",
  "timestamp": "2025-06-23T10:30:00Z",
  "service": "AI Base API",
  "version": "1.0.0"
}
```

### Detailed Health Check ⭐
```http
GET http://localhost:8000/api/v1/health/detailed
```
**Purpose**: Comprehensive system status with all components
```json
{
  "status": "healthy",
  "timestamp": "2025-06-23T10:30:00Z",
  "uptime": "2:15:30",
  "version": "1.0.0",
  "system": {
    "platform": "Windows-10",
    "python_version": "3.12.0",
    "cpu_count": 8,
    "memory_total_gb": 16.0
  },
  "environment": {
    "python_312_plus": {"status": "ok", "current": "3.12.0"},
    "nodejs": {"status": "ok", "version": "v22.16.0"},
    "npm": {"status": "ok", "version": "9.4.1"}
  },
  "database": {
    "connection": {"status": "ok", "message": "Database connection successful"},
    "file": {"status": "ok", "size_mb": 2.5}
  },
  "dependencies": {
    "fastapi": {"status": "ok", "version": "0.104.1"},
    "uvicorn": {"status": "ok", "version": "0.24.0"},
    "sqlalchemy": {"status": "ok", "version": "2.0.23"}
  },
  "performance": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "memory_available_gb": 8.6
  }
}
```

### Database Health Check
```http
GET http://localhost:8000/api/v1/health/database
```
**Purpose**: Database-specific connectivity and performance tests

### System Health Check
```http
GET http://localhost:8000/api/v1/health/system
```
**Purpose**: System resource usage and availability monitoring

### Dependencies Health Check
```http
GET http://localhost:8000/api/v1/health/dependencies
```
**Purpose**: Verify all required and optional dependencies

## 🏗️ Project Structure

```
backend/
├── app/                           # FastAPI application
│   ├── __init__.py               # Application package
│   ├── main.py                   # FastAPI app and health endpoints ⭐
│   ├── api/                      # API endpoints
│   │   ├── __init__.py
│   │   └── health.py             # Health check router ⭐
│   ├── core/                     # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration management ⭐
│   │   └── database.py           # Database setup ⭐
│   ├── models/                   # SQLAlchemy models
│   │   └── __init__.py           # Database models ⭐
│   ├── schemas/                  # Pydantic schemas
│   └── crud/                     # Database operations
├── requirements.txt              # Python dependencies ⭐
├── start_backend.bat             # Windows startup script ⭐
├── start_dev_server.py           # Python startup script ⭐
├── test_health_system.py         # Health check tests ⭐
└── README.md                     # This file
```

## 🔧 Configuration

Configuration is managed through environment variables and `.env` files:

### Database Configuration
```env
# Database Type (sqlite, postgresql, mongodb)
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./databases/ai_base.db

# PostgreSQL (Production)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_base
POSTGRES_USER=ai_user
POSTGRES_PASSWORD=your_secure_password

# MongoDB (NoSQL)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=ai_base
```

### API Configuration
```env
# FastAPI Settings
API_HOST=localhost
API_PORT=8000
FASTAPI_RELOAD=true
FASTAPI_DEBUG=true
FASTAPI_LOG_LEVEL=info

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Security Configuration
```env
# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Session Configuration
SESSION_SECRET_KEY=your_session_secret_here
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
```

## 🌐 Development URLs

| Service               | URL                                          | Description                    |
| --------------------- | -------------------------------------------- | ------------------------------ |
| **Backend API**       | http://localhost:8000                        | Main API endpoint              |
| **API Documentation** | http://localhost:8000/docs                   | Interactive API docs (Swagger) |
| **ReDoc**             | http://localhost:8000/redoc                  | Alternative API documentation  |
| **Basic Health**      | http://localhost:8000/api/v1/health          | Simple health check            |
| **Detailed Health**   | http://localhost:8000/api/v1/health/detailed | Comprehensive health status    |

## 🧪 Testing

### Test Health Check System
```bash
# Test the health check endpoints
python test_health_system.py
```

### Manual Testing
```bash
# Test basic health
curl http://localhost:8000/api/v1/health

# Test detailed health (recommended)
curl http://localhost:8000/api/v1/health/detailed

# Test specific components
curl http://localhost:8000/api/v1/health/database
curl http://localhost:8000/api/v1/health/system
curl http://localhost:8000/api/v1/health/dependencies
```

## 📋 Health Status Levels

| Status      | Description                      | HTTP Code | Action Required  |
| ----------- | -------------------------------- | --------- | ---------------- |
| `healthy`   | All systems operational          | 200       | None             |
| `degraded`  | Minor issues, service functional | 200       | Monitor          |
| `warning`   | Potential issues detected        | 200       | Investigate      |
| `critical`  | Major issues, service impacted   | 503       | Immediate action |
| `unhealthy` | Service unavailable              | 503       | Fix required     |

## 🔍 Monitoring Integration

The health check system integrates with:

### Load Balancers
```yaml
# Example: NGINX health check
upstream backend {
    server localhost:8000;
    health_check uri=/api/v1/health;
}
```

### Monitoring Tools
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **DataDog**: Application monitoring
- **New Relic**: Performance monitoring

### Alerting Systems
- **PagerDuty**: Incident management
- **Slack**: Team notifications
- **Email**: Critical alerts

## 🚀 Production Deployment

### Environment Variables
```env
# Production settings
ENVIRONMENT=production
DEBUG=false
FASTAPI_RELOAD=false

# Security
JWT_SECRET_KEY=your_production_secret_here
SESSION_COOKIE_SECURE=true

# Database
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:password@host:port/database

# Performance
FASTAPI_LOG_LEVEL=warning
```

### Docker Support (Future)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🛠️ Development Workflow

### Adding New Health Checks
1. Edit `app/api/health.py`
2. Add new endpoint function
3. Include in health router
4. Test with `test_health_system.py`

### Database Changes
1. Update models in `app/models/`
2. Generate migration: `alembic revision --autogenerate`
3. Apply migration: `alembic upgrade head`

### Configuration Changes
1. Update `app/core/config.py`
2. Add environment variables to `.env`
3. Document in README

## 📦 Dependencies

### Core Dependencies
- **FastAPI 0.104.1+**: Modern web framework
- **Uvicorn 0.24.0+**: ASGI server
- **SQLAlchemy 2.0.23+**: Database ORM
- **Pydantic 2.5.0+**: Data validation
- **psutil 5.9.0+**: System monitoring

### Optional Dependencies
- **psycopg2-binary**: PostgreSQL support
- **pymongo**: MongoDB support
- **redis**: Caching support
- **structlog**: Structured logging

## 🔧 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Install dependencies
pip install -r requirements.txt
```

**Database Connection Failed**
```bash
# Check database configuration
curl http://localhost:8000/api/v1/health/database
```

**Port Already in Use**
```bash
# Change port in .env or command line
uvicorn app.main:app --port 8001
```

**Health Check Fails**
```bash
# Check detailed health status
curl http://localhost:8000/api/v1/health/detailed
```

## 📖 Next Steps

1. **Frontend Integration**: Connect with React frontend at http://localhost:3000
2. **Authentication**: Implement user authentication and authorization
3. **Database Models**: Add application-specific database models
4. **API Endpoints**: Create business logic endpoints
5. **Testing**: Expand test coverage
6. **Documentation**: Add API endpoint documentation
7. **Deployment**: Set up production deployment pipeline

## 🤝 Contributing

When making changes:

1. Update health checks for new components
2. Add environment configuration as needed
3. Update documentation
4. Test health check endpoints
5. Ensure backward compatibility

---

**Status**: ✅ FastAPI backend with comprehensive health check system  
**Version**: 1.0.0  
**Last Updated**: June 23, 2025
