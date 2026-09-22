from sqlalchemy import Column, Integer, String, Text

from app.database.connection import Base


class Job(Base):

    __tablename__ = "jobs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    pipeline_run_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    title = Column(
        String(200),
        nullable=False
    )

    company = Column(
        String(200),
        nullable=False
    )

    location = Column(
        String(200)
    )

    description = Column(
        Text
    )

    source = Column(
        String(100)
    )

    url = Column(
        String(500)
    )

    salary_min = Column(
        Integer,
        nullable=True
    )

    salary_max = Column(
        Integer,
        nullable=True
    )

    match_score = Column(
        Integer
    )

    priority_score = Column(
        Integer,
        default=0
    )

    status = Column(
        String(50),
        default="ACTIVE"
    )

    discovered_at = Column(
        String(50),
        nullable=True
    )

    last_seen_at = Column(
        String(50),
        nullable=True
    )