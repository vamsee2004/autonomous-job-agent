from sqlalchemy import Column, Integer, String, Text

from app.database.connection import Base


class Application(Base):

    __tablename__ = "applications"

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

    job_id = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(50),
        default="PREPARED"
    )

    mode = Column(
        String(50),
        default="APPROVAL_REQUIRED"
    )

    resume_file = Column(
        String(500),
        nullable=True
    )

    cover_letter_file = Column(
        String(500),
        nullable=True
    )

    applied_at = Column(
        String(50),
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    approval_required = Column(
        Integer,
        default=1
    )

    approved = Column(
        Integer,
        default=0
    )