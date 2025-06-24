# AI Base Project - Documentation Directory

This directory contains comprehensive documentation for the AI Base Project.

## Directory Structure

```text
docs/
├── api/                    # API documentation
│   ├── health-checks.md    # Health check endpoints
│   ├── authentication.md  # Authentication guide
│   └── endpoints.md        # API endpoint reference
├── architecture/           # System architecture
│   ├── overview.md         # System overview
│   ├── database.md         # Database design
│   └── health-system.md    # Health check architecture
├── deployment/             # Deployment guides
│   ├── development.md      # Development setup
│   ├── production.md       # Production deployment
│   └── docker.md           # Docker deployment
├── tutorials/              # Step-by-step tutorials
│   ├── getting-started.md  # Quick start guide
│   ├── health-monitoring.md # Health monitoring setup
│   └── troubleshooting.md  # Common issues and solutions
└── README.md              # This file
```

## Documentation Topics

### 🚀 Quick Start
- Development environment setup
- Running the application
- Basic health check verification
- Frontend and backend integration

### 🏗️ Architecture
- System overview and components
- Health check system design
- Database architecture
- API design patterns

### 🔧 API Reference
- Health check endpoints (`/api/v1/health/*`)
- Authentication and authorization
- Error handling and responses
- Rate limiting and throttling

### 📊 Health Monitoring
- Comprehensive health check system
- System resource monitoring
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
