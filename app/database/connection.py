from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Find the project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Database folder
DATABASE_DIRECTORY = (
    PROJECT_ROOT / "data"
)

# Create data folder if it doesn't exist
DATABASE_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)

# Absolute database path
DATABASE_PATH = (
    DATABASE_DIRECTORY / "jobs.db"
)

DATABASE_URL = (
    f"sqlite:///{DATABASE_PATH}"
)


# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# Database session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for SQLAlchemy models
Base = declarative_base()