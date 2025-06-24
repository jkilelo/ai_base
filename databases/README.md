# AI Base Project - Database Directory

This directory contains database files and database-related scripts for the AI Base Project.

## Directory Structure

```
databases/
├── ai_base.db              # SQLite database file (auto-created)
├── test_ai_base.db         # Test database file (auto-created)
├── backups/                # Database backups (manual/automated)
├── migrations/             # Database migration scripts
├── seeds/                  # Seed data for development
└── README.md              # This file
```

## Database Types Supported

### SQLite (Default for Development)
- **File**: `ai_base.db`
- **Location**: This directory
- **Usage**: Development, testing, small deployments
- **Connection**: `sqlite:///./databases/ai_base.db`

### PostgreSQL (Production)
- **Usage**: Production deployments, high-performance requirements
- **Configuration**: Set via environment variables
- **Connection**: `postgresql://user:password@host:port/database`

### MongoDB (NoSQL Features)
- **Usage**: Document storage, flexible schemas
- **Configuration**: Set via environment variables  
- **Connection**: `mongodb://user:password@host:port/database`

## Health Check Integration

The FastAPI health check system verifies:

✅ **Database Connectivity**: Tests connection to configured database  
✅ **Database File**: Verifies SQLite file exists and is accessible  
✅ **Database Size**: Monitors database file size and growth  
✅ **Query Performance**: Tests basic query execution  
✅ **Connection Pool**: Monitors connection pool status  

## Environment Configuration

Configure database settings in `.env`:

```env
# Database Type
DATABASE_TYPE=sqlite

# SQLite Configuration
DATABASE_URL=sqlite:///./databases/ai_base.db
SQLITE_DATABASE_PATH=./databases/ai_base.db
SQLITE_ECHO=false

# PostgreSQL Configuration (Production)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_base
POSTGRES_USER=ai_user
POSTGRES_PASSWORD=your_secure_password

# MongoDB Configuration (NoSQL)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=ai_base
MONGODB_USER=ai_user
MONGODB_PASSWORD=your_secure_password
```

## Quick Start

### SQLite (Default)
No setup required - database file will be created automatically when the FastAPI application starts.

### PostgreSQL Setup
```bash
# Install PostgreSQL
# Create database and user
createdb ai_base
createuser ai_user
```

### MongoDB Setup  
```bash
# Install MongoDB
# Create database and user through MongoDB shell
```

## Database Health Monitoring

Access health check endpoints:

- **Basic**: `GET /api/v1/health`
- **Database**: `GET /api/v1/health/database` 
- **Detailed**: `GET /api/v1/health/detailed`

Example health check response:
```json
{
  "status": "healthy",
  "database": {
    "connection": "ok",
    "type": "sqlite",
    "file_path": "./databases/ai_base.db",
    "file_size_mb": 2.5
  }
}
```

## Backup and Maintenance

### SQLite Backup
```bash
# Manual backup
cp databases/ai_base.db databases/backups/ai_base_$(date +%Y%m%d_%H%M%S).db

# Automated backup (add to cron)
0 2 * * * cp /path/to/databases/ai_base.db /path/to/databases/backups/ai_base_$(date +\%Y\%m\%d_\%H\%M\%S).db
```

### PostgreSQL Backup
```bash
pg_dump ai_base > databases/backups/ai_base_$(date +%Y%m%d_%H%M%S).sql
```

### MongoDB Backup
```bash
mongodump --db ai_base --out databases/backups/mongodb_$(date +%Y%m%d_%H%M%S)
```

## Security Considerations

🔒 **Access Control**: Use strong passwords and limit database user permissions  
🔒 **Encryption**: Enable encryption at rest for sensitive data  
🔒 **Network Security**: Use SSL/TLS for database connections  
🔒 **Backup Security**: Encrypt and secure database backups  
🔒 **Monitoring**: Monitor database access and query patterns  

## Performance Optimization

⚡ **Indexing**: Add appropriate indexes for frequently queried columns  
⚡ **Connection Pooling**: Configure optimal connection pool size  
⚡ **Query Optimization**: Monitor and optimize slow queries  
⚡ **Caching**: Implement Redis caching for frequently accessed data  
⚡ **Partitioning**: Consider table partitioning for large datasets  

## Migration Management

Database schema changes are managed through Alembic migrations:

```bash
# Generate migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Integration with Health Check System

The health check system provides comprehensive database monitoring:

1. **Connection Health**: Verifies database connectivity
2. **Performance Metrics**: Monitors query response times  
3. **Resource Usage**: Tracks database file size and memory usage
4. **Configuration Validation**: Ensures proper database configuration
5. **Dependency Verification**: Confirms required database drivers are installed

This ensures your application's database layer is healthy and performing optimally.
