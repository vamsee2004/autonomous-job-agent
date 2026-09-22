from datetime import datetime

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.application_feedback import (
    ApplicationFeedback
)


ALLOWED_OUTCOMES = {
    "APPLIED",
    "INTERVIEW",
    "REJECTED",
    "SELECTED",
    "NO_RESPONSE",
    "WITHDRAWN"
}


def create_application_feedback(
    db: Session,
    application_id: int,
    outcome: str,
    feedback: str = None
):
    # ---------------------------------------------
    # Find application
    # ---------------------------------------------

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if not application:

        return {
            "success": False,
            "reason": "APPLICATION_NOT_FOUND"
        }


    # ---------------------------------------------
    # Validate outcome
    # ---------------------------------------------

    normalized_outcome = (
        str(outcome)
        .strip()
        .upper()
    )

    if normalized_outcome not in ALLOWED_OUTCOMES:

        return {
            "success": False,
            "reason": "INVALID_OUTCOME",
            "allowed_outcomes": sorted(
                ALLOWED_OUTCOMES
            )
        }


    # ---------------------------------------------
    # Create feedback record
    # ---------------------------------------------

    feedback_record = ApplicationFeedback(
        application_id=application.id,
        job_id=application.job_id,
        outcome=normalized_outcome,
        feedback=feedback,
        created_at=datetime.now().isoformat()
    )

    db.add(feedback_record)

    db.commit()

    db.refresh(
        feedback_record
    )


    # ---------------------------------------------
    # Return result
    # ---------------------------------------------

    return {
        "success": True,
        "feedback_id": feedback_record.id,
        "application_id": application.id,
        "job_id": application.job_id,
        "outcome": feedback_record.outcome,
        "feedback": feedback_record.feedback,
        "created_at": feedback_record.created_at
    }


def get_application_feedback(
    db: Session,
    application_id: int
):
    records = (
        db.query(ApplicationFeedback)
        .filter(
            ApplicationFeedback.application_id
            == application_id
        )
        .order_by(
            ApplicationFeedback.id.asc()
        )
        .all()
    )

    return records


def get_all_application_feedback(
    db: Session
):
    records = (
        db.query(ApplicationFeedback)
        .order_by(
            ApplicationFeedback.id.desc()
        )
        .all()
    )

    return records