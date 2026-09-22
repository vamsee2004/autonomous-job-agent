from sqlalchemy import Column, Integer, String, Text

from app.database.connection import Base


class Outreach(Base):

    __tablename__ = "outreach"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    application_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    job_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    channel = Column(
        String(50),
        nullable=False,
        default="EMAIL"
    )

    recipient = Column(
        String(255),
        nullable=True
    )

    subject = Column(
        String(255),
        nullable=True
    )

    message = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False,
        default="DRAFT"
    )

    scheduled_at = Column(
        String(50),
        nullable=True
    )

    sent_at = Column(
        String(50),
        nullable=True
    )

    response_status = Column(
        String(50),
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )