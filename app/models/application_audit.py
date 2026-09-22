from sqlalchemy import Column, Integer, String, Text

from app.database.connection import Base


class ApplicationAudit(Base):

    __tablename__ = "application_audits"

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

    action = Column(
        String(100),
        nullable=False
    )

    old_status = Column(
        String(50),
        nullable=True
    )

    new_status = Column(
        String(50),
        nullable=True
    )

    details = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        String(50),
        nullable=False
    )