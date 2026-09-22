from sqlalchemy import Column, Integer, String, Text

from app.database.connection import Base


class PipelineRun(Base):

    __tablename__ = "pipeline_runs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    started_at = Column(
        String(50),
        nullable=False
    )

    completed_at = Column(
        String(50),
        nullable=True
    )

    status = Column(
        String(50),
        default="RUNNING"
    )

    search_title = Column(
        String(200)
    )

    search_location = Column(
        String(200)
    )

    jobs_found = Column(
        Integer,
        default=0
    )

    jobs_saved = Column(
        Integer,
        default=0
    )

    applications_prepared = Column(
        Integer,
        default=0
    )

    error_message = Column(
        Text,
        nullable=True
    )