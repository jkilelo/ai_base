# AI Base Project v1 - Core Configuration
# Centralized configuration management using Pydantic settings

import os
from typing import List, Optional, Any
from functools import lru_cache

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, field_validator, ConfigDict

    PYDANTIC_V2 = True
except ImportError:
    try:
        from pydantic import BaseSettings, Field, validator as field_validator
        from pydantic import BaseSettings as PydanticBaseSettings

        PYDANTIC_V2 = False
        ConfigDict = None
    except ImportError:
        print("❌ Pydantic not available - please install dependencies")
        BaseSettings = object
        Field = lambda **kwargs: None
        field_validator = lambda *args, **kwargs: lambda f: f
        PYDANTIC_V2 = False
        ConfigDict = None


class Settings(BaseSettings):
    """
    Application settings using Pydantic BaseSettings.

    Automatically loads from environment variables and .env files.
    Provides validation and type conversion.
    """

    # API Configuration
    API_TITLE: str = Field(default="AI Base API", description="API title")
    API_DESCRIPTION: str = Field(
        default="FastAPI backend for AI Base Project", description="API description"
    )
    API_VERSION: str = Field(default="1.0.0", description="API version")
    API_HOST: str = Field(default="localhost", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_PREFIX: str = Field(default="/api/v1", description="API prefix")

    # FastAPI Configuration
    FASTAPI_RELOAD: bool = Field(
        default=True, description="Enable auto-reload in development"
    )
    FASTAPI_DEBUG: bool = Field(default=True, description="Enable debug mode")
    FASTAPI_LOG_LEVEL: str = Field(default="info", description="Log level")

    # Database Configuration
    DATABASE_TYPE: str = Field(default="sqlite", description="Database type")
    DATABASE_URL: str = Field(
        default="sqlite:///./ai_base.db", description="Database connection URL"
    )
    SQLITE_DATABASE_PATH: str = Field(
        default="./databases/ai_base.db", description="SQLite database file path"
    )
    SQLITE_ECHO: bool = Field(default=False, description="Enable SQLAlchemy echo")

    # PostgreSQL Configuration (for production)
    POSTGRES_HOST: str = Field(default="localhost", description="PostgreSQL host")
    POSTGRES_PORT: int = Field(default=5432, description="PostgreSQL port")
    POSTGRES_DB: str = Field(default="ai_base", description="PostgreSQL database name")
    POSTGRES_USER: str = Field(default="ai_user", description="PostgreSQL username")
    POSTGRES_PASSWORD: str = Field(default="", description="PostgreSQL password")

    # MongoDB Configuration (for NoSQL features)
    MONGODB_HOST: str = Field(default="localhost", description="MongoDB host")
    MONGODB_PORT: int = Field(default=27017, description="MongoDB port")
    MONGODB_DB: str = Field(default="ai_base", description="MongoDB database name")
    MONGODB_USER: str = Field(default="ai_user", description="MongoDB username")
    MONGODB_PASSWORD: str = Field(default="", description="MongoDB password")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        description="Allowed CORS origins",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True, description="Allow credentials in CORS"
    )
    CORS_ALLOW_METHODS: List[str] = Field(
        default=["*"], description="Allowed HTTP methods"
    )
    CORS_ALLOW_HEADERS: List[str] = Field(
        default=["*"], description="Allowed HTTP headers"
    )

    # Security Configuration
    JWT_SECRET_KEY: str = Field(
        default="your_jwt_secret_key_here_change_in_production",
        description="JWT secret key",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="JWT access token expiration time in minutes"
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="JWT refresh token expiration time in days"
    )

    # Session Configuration
    SESSION_SECRET_KEY: str = Field(
        default="your_session_secret_here", description="Session secret key"
    )
    SESSION_COOKIE_SECURE: bool = Field(
        default=False, description="Use secure cookies (HTTPS only)"
    )
    SESSION_COOKIE_HTTPONLY: bool = Field(default=True, description="HTTP-only cookies")
    SESSION_COOKIE_SAMESITE: str = Field(
        default="lax", description="SameSite cookie policy"
    )

    # Environment Configuration
    ENVIRONMENT: str = Field(default="development", description="Environment")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="info", description="Application log level")
    LOG_FORMAT: str = Field(default="detailed", description="Log format")

    # Testing Configuration
    TESTING: bool = Field(default=False, description="Testing mode")
    TEST_DATABASE_URL: str = Field(
        default="sqlite:///./test_ai_base.db", description="Test database URL"
    )

    # Development Configuration
    HOT_RELOAD: bool = Field(default=True, description="Enable hot reload")
    AUTO_RELOAD: bool = Field(default=True, description="Enable auto reload")
    DEV_TOOLS: bool = Field(
        default=True, description="Enable development tools"
    )  # Version Configuration
    PROJECT_VERSION: str = Field(default="v1", description="Project version")
    PYTHON_VERSION: str = Field(default="3.12", description="Python version")
    NODE_ENV: str = Field(default="development", description="Node environment")

    # Pydantic v2 configuration
    if PYDANTIC_V2:
        model_config = ConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            case_sensitive=True,
            extra="forbid",
        )
    else:

        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"
            case_sensitive = True
            # Look for .env files in multiple locations
            env_file_paths = [
                ".env",
                "../.env",
                "../../.env",
                "../../../.env",
            ] @ field_validator("CORS_ORIGINS", mode="before")

    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v):
        """Validate and construct database URL based on type."""
        # Simplified validation for Pydantic v2
        if v.startswith("sqlite:///"):
            db_path = v.replace("sqlite:///", "")
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return v

    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.lower() @ field_validator("ENVIRONMENT")

    @classmethod
    def validate_environment(cls, v):
        """Validate environment."""
        valid_envs = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v.lower()

    def get_database_url(self) -> str:
        """Get the appropriate database URL for the current environment."""
        if self.TESTING:
            return self.TEST_DATABASE_URL
        return self.DATABASE_URL

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"

    def is_testing(self) -> bool:
        """Check if running in testing mode."""
        return self.TESTING or self.ENVIRONMENT == "testing"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache to ensure settings are loaded only once
    and reused throughout the application lifecycle.
    """
    return Settings()


# Configuration validation
def validate_configuration():
    """Validate configuration and environment setup."""
    settings = get_settings()

    errors = []
    warnings = []

    # Security checks
    if settings.is_production():
        if settings.JWT_SECRET_KEY == "your_jwt_secret_key_here_change_in_production":
            errors.append("JWT_SECRET_KEY must be changed in production")

        if settings.SESSION_SECRET_KEY == "your_session_secret_here":
            errors.append("SESSION_SECRET_KEY must be changed in production")

        if not settings.SESSION_COOKIE_SECURE:
            warnings.append("SESSION_COOKIE_SECURE should be True in production")

        if settings.DEBUG:
            warnings.append("DEBUG should be False in production")

    # Database checks
    if settings.DATABASE_TYPE == "sqlite":
        db_path = settings.SQLITE_DATABASE_PATH
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                warnings.append(f"Created database directory: {db_dir}")
            except Exception as e:
                errors.append(f"Cannot create database directory {db_dir}: {e}")

    # CORS checks
    if settings.is_production() and "*" in settings.CORS_ORIGINS:
        warnings.append("Wildcard CORS origins should not be used in production")

    return {"errors": errors, "warnings": warnings}


# Export settings instance
settings = get_settings()
