"""Test Database Configuration - SQLite for local testing."""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use SQLite for testing when no PostgreSQL is available
TESTING = os.getenv("TESTING", "true").lower() == "true"

if TESTING:
    DATABASE_URL = "sqlite:///./gcdtp_test.db"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@database:5432/gcdtp"
    )

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if TESTING else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
