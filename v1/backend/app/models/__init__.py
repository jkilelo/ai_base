# AI Base Project v1 - Database Models
# SQLAlchemy models for the application

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func

from ..core.database import Base


class HealthCheck(Base):
    """
    Health check log model.

    Stores health check results for monitoring and analysis.
    """

    __tablename__ = "health_checks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status = Column(String(50), nullable=False)  # healthy, degraded, unhealthy
    check_type = Column(String(100), nullable=False)  # database, system, dependencies
    details = Column(Text, nullable=True)  # JSON string with detailed results
    response_time_ms = Column(Float, nullable=True)  # Response time in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return (
            f"<HealthCheck(id={self.id}, status={self.status}, type={self.check_type})>"
        )


class SystemMetrics(Base):
    """
    System metrics model.

    Stores system performance metrics for monitoring.
    """

    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # CPU metrics
    cpu_percent = Column(Float, nullable=True)
    cpu_count = Column(Integer, nullable=True)

    # Memory metrics
    memory_total_gb = Column(Float, nullable=True)
    memory_used_gb = Column(Float, nullable=True)
    memory_available_gb = Column(Float, nullable=True)
    memory_percent = Column(Float, nullable=True)

    # Disk metrics
    disk_total_gb = Column(Float, nullable=True)
    disk_used_gb = Column(Float, nullable=True)
    disk_free_gb = Column(Float, nullable=True)
    disk_percent = Column(Float, nullable=True)

    # Database metrics
    database_size_mb = Column(Float, nullable=True)
    database_connection_count = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<SystemMetrics(id={self.id}, cpu={self.cpu_percent}%, memory={self.memory_percent}%)>"


class ApiLog(Base):
    """
    API request log model.

    Stores API request logs for monitoring and analysis.
    """

    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Request information
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    path = Column(String(500), nullable=False)
    query_params = Column(Text, nullable=True)
    headers = Column(Text, nullable=True)  # JSON string

    # Response information
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)

    # Client information
    client_ip = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)

    # Error information
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ApiLog(id={self.id}, method={self.method}, path={self.path}, status={self.status_code})>"


class Configuration(Base):
    """
    Configuration settings model.

    Stores application configuration that can be modified at runtime.
    """

    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    data_type = Column(
        String(50), nullable=False, default="string"
    )  # string, integer, float, boolean, json
    is_sensitive = Column(Boolean, default=False)  # Hide from logs/API responses
    is_readonly = Column(Boolean, default=False)  # Prevent modifications
    category = Column(String(100), nullable=True)  # Group related settings

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Configuration(key={self.key}, type={self.data_type})>"


# Export all models
__all__ = ["Base", "HealthCheck", "SystemMetrics", "ApiLog", "Configuration"]
