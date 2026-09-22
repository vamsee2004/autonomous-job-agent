from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


DATABASE_DIRECTORY = (
    PROJECT_ROOT
    / "data"
)


DATABASE_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


DATABASE_PATH = (
    DATABASE_DIRECTORY
    / "jobs.db"
)


DATABASE_URL = (
    f"sqlite:///{DATABASE_PATH}"
)


# ============================================================
# DATABASE ENGINE
# ============================================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# ============================================================
# DATABASE SESSION
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# DATABASE BASE
# ============================================================

Base = declarative_base()


# ============================================================
# SAFE DATABASE SESSION
# ============================================================

def get_safe_session():

    db = SessionLocal()

    try:

        yield db

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()