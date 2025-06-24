# AI Base Project v1 - Health Check API Router
# Dedicated router for health check endpoints

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_database_session, check_database_connection
from ..core.config import get_settings

# Create router
router = APIRouter(
    prefix="/health",
    tags=["health"],
    responses={
        200: {"description": "Health check successful"},
        503: {"description": "Service unavailable"},
    },
)

# Get settings
settings = get_settings()


@router.get("/")
async def basic_health():
    """
    Basic health check endpoint.

    Returns simple status to verify API is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Base API",
        "version": "1.0.0",
    }


@router.get("/detailed")
async def detailed_health():
    """
    Detailed health check endpoint.

    Provides comprehensive system status including:
    - Database connectivity
    - System resources
    - Configuration status
    - Dependencies status
    """
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "AI Base API",
            "version": "1.0.0",
            "checks": {},
        }

        # Database health check
        db_healthy = check_database_connection()
        health_data["checks"]["database"] = {
            "status": "ok" if db_healthy else "error",
            "message": (
                "Database connection successful"
                if db_healthy
                else "Database connection failed"
            ),
            "type": settings.DATABASE_TYPE,
            "url_masked": (
                "***" + settings.DATABASE_URL[-20:]
                if len(settings.DATABASE_URL) > 20
                else "***"
            ),
        }

        # Configuration health check
        config_issues = []

        # Check critical configuration
        if settings.JWT_SECRET_KEY == "your_jwt_secret_key_here_change_in_production":
            config_issues.append("JWT secret key not configured")

        if not settings.CORS_ORIGINS:
            config_issues.append("CORS origins not configured")

        health_data["checks"]["configuration"] = {
            "status": "ok" if not config_issues else "warning",
            "message": (
                "Configuration OK"
                if not config_issues
                else f"Issues: {', '.join(config_issues)}"
            ),
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
        }

        # System checks
        import os
        import psutil

        # Memory check
        memory = psutil.virtual_memory()
        health_data["checks"]["memory"] = {
            "status": (
                "ok"
                if memory.percent < 80
                else "warning" if memory.percent < 90 else "critical"
            ),
            "usage_percent": memory.percent,
            "available_gb": round(memory.available / (1024**3), 2),
            "total_gb": round(memory.total / (1024**3), 2),
        }

        # Disk check
        disk = psutil.disk_usage("/")
        health_data["checks"]["disk"] = {
            "status": (
                "ok"
                if disk.percent < 80
                else "warning" if disk.percent < 90 else "critical"
            ),
            "usage_percent": disk.percent,
            "free_gb": round(disk.free / (1024**3), 2),
            "total_gb": round(disk.total / (1024**3), 2),
        }

        # Dependencies check
        dependencies = {}

        # Check FastAPI
        try:
            import fastapi

            dependencies["fastapi"] = {"status": "ok", "version": fastapi.__version__}
        except ImportError:
            dependencies["fastapi"] = {"status": "error", "version": "not installed"}

        # Check Uvicorn
        try:
            import uvicorn

            dependencies["uvicorn"] = {"status": "ok", "version": uvicorn.__version__}
        except ImportError:
            dependencies["uvicorn"] = {"status": "error", "version": "not installed"}

        # Check SQLAlchemy
        try:
            import sqlalchemy

            dependencies["sqlalchemy"] = {
                "status": "ok",
                "version": sqlalchemy.__version__,
            }
        except ImportError:
            dependencies["sqlalchemy"] = {"status": "error", "version": "not installed"}

        # Check Pydantic
        try:
            import pydantic

            dependencies["pydantic"] = {"status": "ok", "version": pydantic.__version__}
        except ImportError:
            dependencies["pydantic"] = {"status": "error", "version": "not installed"}

        health_data["checks"]["dependencies"] = dependencies

        # Determine overall status
        overall_status = "healthy"

        # Check for critical issues
        if not db_healthy:
            overall_status = "unhealthy"
        elif any(
            check.get("status") == "critical"
            for check in health_data["checks"].values()
            if isinstance(check, dict)
        ):
            overall_status = "critical"
        elif any(
            check.get("status") == "error"
            for check in health_data["checks"].values()
            if isinstance(check, dict)
        ):
            overall_status = "degraded"
        elif any(
            check.get("status") == "warning"
            for check in health_data["checks"].values()
            if isinstance(check, dict)
        ):
            overall_status = "warning"

        health_data["status"] = overall_status

        # Return appropriate HTTP status
        if overall_status in ["unhealthy", "critical"]:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=health_data
            )

        return health_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Health check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/database")
async def database_health(db: Session = Depends(get_database_session)):
    """
    Database-specific health check.

    Tests database connectivity and basic operations.
    """
    try:
        # Test basic query
        result = db.execute("SELECT 1 as test").fetchone()

        # Get database info
        from ..core.database import get_database_info

        db_info = get_database_info()

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "connection": "ok",
                "test_query": bool(result),
                "type": db_info["type"],
                "connection_status": db_info["connection_status"],
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": {"connection": "error", "error": str(e)},
            },
        )


@router.get("/system")
async def system_health():
    """
    System resource health check.

    Returns system resource usage and availability.
    """
    try:
        import psutil
        import platform
        import sys

        # System information
        system_info = {
            "platform": platform.platform(),
            "python_version": sys.version,
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
        }

        # Memory information
        memory = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent,
            "status": (
                "ok"
                if memory.percent < 80
                else "warning" if memory.percent < 90 else "critical"
            ),
        }

        # Disk information
        disk = psutil.disk_usage("/")
        disk_info = {
            "total_gb": round(disk.total / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent": disk.percent,
            "status": (
                "ok"
                if disk.percent < 80
                else "warning" if disk.percent < 90 else "critical"
            ),
        }

        # Determine overall system status
        system_status = "healthy"
        if memory_info["status"] == "critical" or disk_info["status"] == "critical":
            system_status = "critical"
        elif memory_info["status"] == "warning" or disk_info["status"] == "warning":
            system_status = "warning"

        return {
            "status": system_status,
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_info,
            "memory": memory_info,
            "disk": disk_info,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"System health check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/dependencies")
async def dependencies_health():
    """
    Dependencies health check.

    Verifies all required dependencies are installed and accessible.
    """
    try:
        dependencies = {}

        # Critical dependencies
        critical_deps = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("sqlalchemy", "Database ORM"),
            ("pydantic", "Data validation"),
            ("psutil", "System monitoring"),
        ]

        for dep_name, description in critical_deps:
            try:
                module = __import__(dep_name)
                version = getattr(module, "__version__", "unknown")
                dependencies[dep_name] = {
                    "status": "ok",
                    "version": version,
                    "description": description,
                }
            except ImportError:
                dependencies[dep_name] = {
                    "status": "error",
                    "version": "not installed",
                    "description": description,
                }

        # Optional dependencies
        optional_deps = [
            ("redis", "Caching support"),
            ("pymongo", "MongoDB support"),
            ("psycopg2", "PostgreSQL support"),
        ]

        for dep_name, description in optional_deps:
            try:
                module = __import__(dep_name)
                version = getattr(module, "__version__", "unknown")
                dependencies[dep_name] = {
                    "status": "ok",
                    "version": version,
                    "description": description,
                    "optional": True,
                }
            except ImportError:
                dependencies[dep_name] = {
                    "status": "missing",
                    "version": "not installed",
                    "description": description,
                    "optional": True,
                }

        # Determine overall dependencies status
        critical_missing = [
            dep
            for dep, info in dependencies.items()
            if info["status"] == "error" and not info.get("optional", False)
        ]

        if critical_missing:
            deps_status = "critical"
        else:
            deps_status = "healthy"

        return {
            "status": deps_status,
            "timestamp": datetime.utcnow().isoformat(),
            "dependencies": dependencies,
            "summary": {
                "total": len(dependencies),
                "installed": len(
                    [d for d in dependencies.values() if d["status"] == "ok"]
                ),
                "missing_critical": critical_missing,
                "missing_optional": [
                    dep
                    for dep, info in dependencies.items()
                    if info["status"] == "missing" and info.get("optional", False)
                ],
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"Dependencies health check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
