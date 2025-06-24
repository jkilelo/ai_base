# AI Base Project v1 - Database Configuration
# SQLAlchemy database setup with support for SQLite, PostgreSQL, and MongoDB

import os
from typing import Generator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .config import get_settings

# Get settings
settings = get_settings()

# Database URL
DATABASE_URL = settings.get_database_url()

# SQLAlchemy engine configuration
if settings.DATABASE_TYPE == "sqlite":
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        echo=settings.SQLITE_ECHO,
        connect_args={
            "check_same_thread": False,  # Allow SQLite to be used with multiple threads
        },
        poolclass=StaticPool,  # Use static pool for SQLite
    )
elif settings.DATABASE_TYPE == "postgresql":
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        echo=settings.SQLITE_ECHO,
        pool_size=20,  # Connection pool size
        max_overflow=0,  # Maximum overflow connections
        pool_pre_ping=True,  # Validate connections before use
        pool_recycle=300,  # Recycle connections every 5 minutes
    )
else:
    # Default to SQLite
    engine = create_engine(
        DATABASE_URL,
        echo=settings.SQLITE_ECHO,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Metadata for table creation
metadata = MetaData()


def get_database_session() -> Generator[Session, None, None]:
    """
    Dependency to get database session.

    Yields:
        Session: SQLAlchemy database session

    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_database_session)):
            return crud.get_items(db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def drop_tables():
    """Drop all database tables."""
    Base.metadata.drop_all(bind=engine)
    print("✅ Database tables dropped successfully")


def reset_database():
    """Reset database by dropping and recreating all tables."""
    print("🔄 Resetting database...")
    drop_tables()
    create_tables()
    print("✅ Database reset completed")


def check_database_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        db = SessionLocal()
        # Test connection with a simple query
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def get_database_info() -> dict:
    """
    Get database information and statistics.

    Returns:
        dict: Database information including type, URL, and statistics
    """
    info = {
        "type": settings.DATABASE_TYPE,
        "url": DATABASE_URL,
        "echo": settings.SQLITE_ECHO,
        "connection_status": check_database_connection(),
    }

    # Add SQLite-specific information
    if settings.DATABASE_TYPE == "sqlite":
        db_path = DATABASE_URL.replace("sqlite:///", "")
        info.update(
            {
                "file_path": db_path,
                "file_exists": os.path.exists(db_path),
                "file_size_bytes": (
                    os.path.getsize(db_path) if os.path.exists(db_path) else 0
                ),
            }
        )

        # Calculate file size in human-readable format
        if info["file_size_bytes"] > 0:
            size_mb = round(info["file_size_bytes"] / (1024 * 1024), 2)
            info["file_size_mb"] = size_mb

    # Add PostgreSQL-specific information
    elif settings.DATABASE_TYPE == "postgresql":
        info.update(
            {
                "host": settings.POSTGRES_HOST,
                "port": settings.POSTGRES_PORT,
                "database": settings.POSTGRES_DB,
                "user": settings.POSTGRES_USER,
            }
        )

    return info


class DatabaseManager:
    """Database manager for handling database operations."""

    def __init__(self):
        self.engine = engine
        self.session_factory = SessionLocal

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.session_factory()

    def create_tables(self):
        """Create all tables."""
        create_tables()

    def drop_tables(self):
        """Drop all tables."""
        drop_tables()

    def reset_database(self):
        """Reset the database."""
        reset_database()

    def check_connection(self) -> bool:
        """Check database connection."""
        return check_database_connection()

    def get_info(self) -> dict:
        """Get database information."""
        return get_database_info()

    def execute_raw_query(self, query: str) -> list:
        """
        Execute a raw SQL query.

        Args:
            query (str): SQL query to execute

        Returns:
            list: Query results
        """
        with self.get_session() as db:
            result = db.execute(query)
            return result.fetchall()

    def get_table_names(self) -> list:
        """Get list of all table names in the database."""
        try:
            with self.get_session() as db:
                if settings.DATABASE_TYPE == "sqlite":
                    result = db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                elif settings.DATABASE_TYPE == "postgresql":
                    result = db.execute(
                        "SELECT tablename FROM pg_tables WHERE schemaname='public'"
                    )
                else:
                    return []

                return [row[0] for row in result.fetchall()]
        except Exception as e:
            print(f"❌ Error getting table names: {e}")
            return []

    def get_table_count(self, table_name: str) -> int:
        """
        Get row count for a specific table.

        Args:
            table_name (str): Name of the table

        Returns:
            int: Number of rows in the table
        """
        try:
            with self.get_session() as db:
                result = db.execute(f"SELECT COUNT(*) FROM {table_name}")
                return result.fetchone()[0]
        except Exception as e:
            print(f"❌ Error getting table count for {table_name}: {e}")
            return 0


# Global database manager instance
db_manager = DatabaseManager()


# Initialize database
def init_database():
    """Initialize database with tables and basic configuration."""
    try:
        # Create database directory if it doesn't exist (for SQLite)
        if settings.DATABASE_TYPE == "sqlite":
            db_path = DATABASE_URL.replace("sqlite:///", "")
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                print(f"✅ Created database directory: {db_dir}")

        # Check connection
        if not check_database_connection():
            raise Exception("Failed to connect to database")

        # Create tables
        create_tables()

        print("✅ Database initialized successfully")

        # Print database info
        info = get_database_info()
        print(f"📊 Database type: {info['type']}")
        if info["type"] == "sqlite":
            print(f"📁 Database file: {info['file_path']}")
            if info["file_exists"]:
                print(f"📊 File size: {info.get('file_size_mb', 0)} MB")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


# Export key components
__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_database_session",
    "create_tables",
    "drop_tables",
    "reset_database",
    "check_database_connection",
    "get_database_info",
    "DatabaseManager",
    "db_manager",
    "init_database",
]
