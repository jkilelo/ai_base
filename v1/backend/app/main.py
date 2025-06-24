# AI Base Project v1 - FastAPI Backend Entry Point
# Health Check & System Verification API

import asyncio
import os
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sqlite3
import subprocess

# Import with graceful fallback
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil not available - system monitoring will be limited")

try:
    from fastapi import FastAPI, HTTPException, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("❌ FastAPI not available - please install dependencies")

if FASTAPI_AVAILABLE:
    from .core.config import get_settings
    from .core.database import engine, SessionLocal
    from .api.health import router as health_router

if not FASTAPI_AVAILABLE:
    print("❌ FastAPI dependencies not installed!")
    print("Please install dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="AI Base API",
    description="FastAPI backend for AI Base Project with comprehensive health checks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Get settings
settings = get_settings()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "AI Base Project API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "detailed_health": "/api/v1/health/detailed",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and perform startup checks."""
    try:
        # Create database tables if they don't exist
        from .models import Base

        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")  # Verify database connection
        db = SessionLocal()
        try:
            from sqlalchemy import text

            db.execute(text("SELECT 1"))
            print("✅ Database connection verified")
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Startup error: {e}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    print("🔄 Shutting down AI Base API...")


# Health check models
class HealthResponse(BaseModel):
    """Basic health check response model."""

    status: str = Field(..., description="API health status")
    timestamp: str = Field(..., description="Current timestamp")
    uptime: str = Field(..., description="API uptime")
    version: str = Field(..., description="API version")


class DetailedHealthResponse(BaseModel):
    """Detailed health check response model."""

    status: str = Field(..., description="Overall health status")
    timestamp: str = Field(..., description="Current timestamp")
    uptime: str = Field(..., description="API uptime")
    version: str = Field(..., description="API version")
    system: Dict[str, Any] = Field(..., description="System information")
    environment: Dict[str, Any] = Field(..., description="Environment information")
    database: Dict[str, Any] = Field(..., description="Database status")
    dependencies: Dict[str, Any] = Field(..., description="Dependency status")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")
    checks: Dict[str, Any] = Field(..., description="Health check results")


# Store startup time for uptime calculation
startup_time = datetime.utcnow()


# Basic health check endpoint
@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.

    Returns simple status information to verify the API is running.
    """
    uptime = datetime.utcnow() - startup_time

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        uptime=str(uptime),
        version="1.0.0",
    )


# Detailed health check endpoint
@app.get("/api/v1/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """
    Comprehensive health check endpoint.

    Verifies all system components including:
    - Python environment and version
    - Node.js and npm availability
    - Database connectivity
    - System resources
    - Dependencies
    - Performance metrics
    """
    try:
        uptime = datetime.utcnow() - startup_time

        # System information
        system_info = {
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_usage": {
                "total_gb": round(psutil.disk_usage("/").total / (1024**3), 2),
                "free_gb": round(psutil.disk_usage("/").free / (1024**3), 2),
                "used_percent": psutil.disk_usage("/").percent,
            },
        }

        # Environment checks
        environment_info = await check_environment()

        # Database checks
        database_info = await check_database()

        # Dependency checks
        dependency_info = await check_dependencies()

        # Performance metrics
        performance_info = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": round(
                psutil.virtual_memory().available / (1024**3), 2
            ),
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
        }

        # Health checks
        health_checks = await perform_health_checks()

        # Determine overall status
        overall_status = "healthy"
        if any(check.get("status") == "error" for check in health_checks.values()):
            overall_status = "unhealthy"
        elif any(check.get("status") == "warning" for check in health_checks.values()):
            overall_status = "degraded"

        return DetailedHealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            uptime=str(uptime),
            version="1.0.0",
            system=system_info,
            environment=environment_info,
            database=database_info,
            dependencies=dependency_info,
            performance=performance_info,
            checks=health_checks,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {str(e)}",
        )


async def check_environment() -> Dict[str, Any]:
    """Check environment variables and configuration."""
    env_checks = {}

    # Python version check
    python_version = sys.version_info
    env_checks["python_312_plus"] = {
        "status": "ok" if python_version >= (3, 12) else "warning",
        "current": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
        "required": "3.12+",
        "message": "Python 3.12+ recommended for best performance",
    }

    # Node.js check
    try:
        node_result = subprocess.run(
            ["node", "--version"], capture_output=True, text=True, timeout=5
        )
        if node_result.returncode == 0:
            node_version = node_result.stdout.strip()
            env_checks["nodejs"] = {
                "status": "ok",
                "version": node_version,
                "message": "Node.js available",
            }
        else:
            env_checks["nodejs"] = {
                "status": "warning",
                "message": "Node.js not found or not accessible",
            }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        env_checks["nodejs"] = {
            "status": "warning",
            "message": "Node.js not found or not accessible",
        }

    # npm check
    try:
        npm_result = subprocess.run(
            ["npm", "--version"], capture_output=True, text=True, timeout=5
        )
        if npm_result.returncode == 0:
            npm_version = npm_result.stdout.strip()
            env_checks["npm"] = {
                "status": "ok",
                "version": npm_version,
                "message": "npm available",
            }
        else:
            env_checks["npm"] = {
                "status": "warning",
                "message": "npm not found or not accessible",
            }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        env_checks["npm"] = {
            "status": "warning",
            "message": "npm not found or not accessible",
        }

    # Environment variables
    required_env_vars = ["DATABASE_URL", "API_HOST", "API_PORT", "CORS_ORIGINS"]

    for var in required_env_vars:
        value = os.getenv(var)
        env_checks[f"env_{var.lower()}"] = {
            "status": "ok" if value else "warning",
            "set": bool(value),
            "message": f"Environment variable {var} {'is set' if value else 'is not set'}",
        }

    return env_checks


async def check_database() -> Dict[str, Any]:
    """Check database connectivity and status."""
    db_info = {}

    try:  # Check database connection
        db = SessionLocal()
        try:
            # Test basic query
            from sqlalchemy import text

            result = db.execute(text("SELECT 1 as test")).fetchone()
            db_info["connection"] = {
                "status": "ok",
                "message": "Database connection successful",
                "test_query": bool(result),
            }

            # Check if we can access database path (for SQLite)
            database_url = settings.DATABASE_URL
            if database_url.startswith("sqlite"):
                db_path = database_url.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    db_size = os.path.getsize(db_path)
                    db_info["file"] = {
                        "status": "ok",
                        "path": db_path,
                        "size_bytes": db_size,
                        "size_mb": round(db_size / (1024 * 1024), 2),
                        "message": "Database file accessible",
                    }
                else:
                    db_info["file"] = {
                        "status": "warning",
                        "path": db_path,
                        "message": "Database file will be created on first use",
                    }

        finally:
            db.close()

    except Exception as e:
        db_info["connection"] = {
            "status": "error",
            "message": f"Database connection failed: {str(e)}",
        }

    return db_info


async def check_dependencies() -> Dict[str, Any]:
    """Check critical dependencies."""
    deps = {}

    # Check FastAPI
    try:
        import fastapi

        deps["fastapi"] = {
            "status": "ok",
            "version": fastapi.__version__,
            "message": "FastAPI available",
        }
    except ImportError:
        deps["fastapi"] = {"status": "error", "message": "FastAPI not installed"}

    # Check Uvicorn
    try:
        import uvicorn

        deps["uvicorn"] = {
            "status": "ok",
            "version": uvicorn.__version__,
            "message": "Uvicorn available",
        }
    except ImportError:
        deps["uvicorn"] = {"status": "error", "message": "Uvicorn not installed"}

    # Check SQLAlchemy
    try:
        import sqlalchemy

        deps["sqlalchemy"] = {
            "status": "ok",
            "version": sqlalchemy.__version__,
            "message": "SQLAlchemy available",
        }
    except ImportError:
        deps["sqlalchemy"] = {"status": "error", "message": "SQLAlchemy not installed"}

    # Check Pydantic
    try:
        import pydantic

        deps["pydantic"] = {
            "status": "ok",
            "version": pydantic.__version__,
            "message": "Pydantic available",
        }
    except ImportError:
        deps["pydantic"] = {"status": "error", "message": "Pydantic not installed"}

    # Check psutil
    try:
        deps["psutil"] = {
            "status": "ok",
            "version": psutil.__version__,
            "message": "psutil available for system monitoring",
        }
    except ImportError:
        deps["psutil"] = {
            "status": "warning",
            "message": "psutil not available - system monitoring limited",
        }

    return deps


async def perform_health_checks() -> Dict[str, Any]:
    """Perform comprehensive health checks."""
    checks = {}

    # File system checks
    project_root = Path(__file__).parent.parent.parent.parent

    # Check important directories
    important_dirs = [
        ("frontend", project_root / "frontend"),
        ("databases", project_root.parent / "databases"),
        ("docs", project_root.parent / "docs"),
        ("shared", project_root.parent / "shared"),
        ("config", project_root.parent / "config"),
    ]

    for name, path in important_dirs:
        checks[f"directory_{name}"] = {
            "status": "ok" if path.exists() else "warning",
            "path": str(path),
            "exists": path.exists(),
            "message": f"Directory {name} {'exists' if path.exists() else 'does not exist'}",
        }

    # Check critical files
    critical_files = [
        ("package_json", project_root / "frontend" / "package.json"),
        ("env_file", project_root.parent / ".env"),
        ("requirements", project_root / "backend" / "requirements.txt"),
    ]

    for name, file_path in critical_files:
        checks[f"file_{name}"] = {
            "status": "ok" if file_path.exists() else "warning",
            "path": str(file_path),
            "exists": file_path.exists(),
            "message": f"File {name} {'exists' if file_path.exists() else 'does not exist'}",
        }

    # Memory usage check
    memory = psutil.virtual_memory()
    checks["memory_usage"] = {
        "status": (
            "ok"
            if memory.percent < 80
            else "warning" if memory.percent < 90 else "error"
        ),
        "percent": memory.percent,
        "available_gb": round(memory.available / (1024**3), 2),
        "message": f"Memory usage at {memory.percent}%",
    }

    # Disk space check
    disk = psutil.disk_usage("/")
    checks["disk_space"] = {
        "status": (
            "ok" if disk.percent < 80 else "warning" if disk.percent < 90 else "error"
        ),
        "percent": disk.percent,
        "free_gb": round(disk.free / (1024**3), 2),
        "message": f"Disk usage at {disk.percent}%",
    }

    return checks


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.FASTAPI_RELOAD,
        log_level=settings.FASTAPI_LOG_LEVEL.lower(),
    )
