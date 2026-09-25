import time
import logging
from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings

logger = logging.getLogger("sih26191.db")

# Engine initialization
engine = create_engine(
    settings.sync_database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> Dict[str, Any]:
    """
    Safely ping the PostgreSQL / PostGIS database to verify connectivity.
    Does not raise unhandled exceptions.
    """
    start_time = time.perf_counter()
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
            # Check PostGIS extension
            postgis_version = "not installed"
            try:
                res = connection.execute(text("SELECT PostGIS_Version();")).scalar()
                if res:
                    postgis_version = str(res)
            except Exception:
                postgis_version = "not available"

            return {
                "connected": True,
                "latency_ms": latency_ms,
                "postgis_version": postgis_version,
                "detail": "Database connection healthy",
            }
    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning(f"Database connectivity check warning: {e}")
        return {
            "connected": False,
            "latency_ms": latency_ms,
            "postgis_version": None,
            "detail": f"Database unreachable or initializing: {str(e)}",
        }
