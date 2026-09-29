"""Database connection and session factory supporting Neon PostgreSQL and local fallback."""
from pathlib import Path
from typing import Tuple
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base
from utils.config import config
from utils.logging import logger

_engine = None
_SessionFactory = None


def get_connection_info() -> Tuple[str, bool]:
    """Return database dialect name and whether it is a live Neon PostgreSQL connection."""
    db_url = config.database_url
    if db_url and db_url.startswith(("postgresql://", "postgres://")):
        return "Neon PostgreSQL", True
    return "Local SQLite (Configurable to Neon)", False


def get_engine():
    """Create or return existing SQLAlchemy engine."""
    global _engine, _SessionFactory
    db_url = config.database_url

    if not db_url or not db_url.strip():
        # Fallback to local SQLite storage
        local_dir = Path(__file__).resolve().parent.parent / "local_storage"
        local_dir.mkdir(exist_ok=True)
        sqlite_path = local_dir / "agent.db"
        sqlite_url = f"sqlite:///{sqlite_path.as_posix()}"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        return engine

    # Neon PostgreSQL connection
    # Normalize postgres:// to postgresql:// for SQLAlchemy 2.0
    if db_url.startswith("postgres://"):
        db_url = "postgresql://" + db_url[len("postgres://"):]

    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"sslmode": "require"} if "sslmode" not in db_url and "neon.tech" in db_url else {}
    )
    return engine


def get_db_session() -> Session:
    """Return a new database session."""
    engine = get_engine()
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return session_factory()


def init_db():
    """Initialize database tables."""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {str(e)}")
        raise


def test_db_connection() -> Tuple[bool, str]:
    """
    Test database connection safely.
    Returns (success: bool, safe_message: str).
    Does NOT leak password or raw secret.
    """
    db_url = config.database_url
    if not db_url or not db_url.strip():
        return False, "DATABASE_URL is not set in configuration."

    try:
        # Check URL protocol
        if not (db_url.startswith("postgresql://") or db_url.startswith("postgres://")):
            return False, "DATABASE_URL must start with postgresql:// or postgres://"

        # Create quick test engine with low timeout
        test_url = db_url
        if test_url.startswith("postgres://"):
            test_url = "postgresql://" + test_url[len("postgres://"):]

        connect_args = {"connect_timeout": 5}
        if "sslmode" not in test_url and "neon.tech" in test_url:
            connect_args["sslmode"] = "require"

        temp_engine = create_engine(
            test_url,
            pool_pre_ping=True,
            connect_args=connect_args
        )
        with temp_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Successfully connected to Neon PostgreSQL database."
    except Exception as e:
        err_msg = str(e)
        # Sanitize any password occurrence in error message
        if "@" in err_msg and "://" in err_msg:
            err_msg = "Database connection error (credentials or network unreachable)."
        return False, f"Connection failed: {err_msg}"
