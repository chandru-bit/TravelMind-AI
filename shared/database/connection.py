import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from sqlalchemy.exc import OperationalError, DBAPIError, InterfaceError
from shared.errors.handlers import APIException

# Fetch database URL from environment or default to local SQLite for simplicity/fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travelmind.db")

# Adjust engine parameters based on database dialect (PostgreSQL vs SQLite)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """FastAPI DB dependency yielding a scoped database session."""
    db = None
    try:
        db = SessionLocal()
        yield db
    except (OperationalError, DBAPIError, InterfaceError) as e:
        import logging
        logging.getLogger("travelmind.database").error(f"Database operational error: {e}")
        raise APIException(
            "SERVICE_UNAVAILABLE",
            "Authentication database service is currently unavailable. Please try again later.",
            503
        )
    finally:
        if db is not None:
            db.close()
