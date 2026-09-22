from sqlalchemy import Column, Integer, String, Text

from app.database.connection import Base


class ApplicationFeedback(Base):

    __tablename__ = "application_feedback"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    application_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    job_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    outcome = Column(
        String(50),
        nullable=False
    )

    feedback = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        String(50),
        nullable=False
    )