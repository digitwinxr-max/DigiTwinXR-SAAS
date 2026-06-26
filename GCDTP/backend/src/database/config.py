"""Database configuration and connection management."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import Base from models.base to ensure all models use the same Base
from ..models.base import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@database:5432/gcdtp"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
