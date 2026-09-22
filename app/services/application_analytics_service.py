from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.application import Application
from app.models.application_feedback import (
    ApplicationFeedback
)


def get_application_analytics(
    db: Session
):
    # =============================================
    # JOB STATISTICS
    # =============================================

    total_jobs = (
        db.query(Job)
        .count()
    )

    active_jobs = (
        db.query(Job)
        .filter(
            Job.status == "ACTIVE"
        )
        .count()
    )

    stale_jobs = (
        db.query(Job)
        .filter(
            Job.status == "STALE"
        )
        .count()
    )

    # =============================================
    # APPLICATION STATISTICS
    # =============================================

    total_applications = (
        db.query(Application)
        .count()
    )

    pending_approval = (
        db.query(Application)
        .filter(
            Application.status
            == "PENDING_APPROVAL"
        )
        .count()
    )

    approved_applications = (
        db.query(Application)
        .filter(
            Application.status
            == "APPROVED"
        )
        .count()
    )

    submitted_applications = (
        db.query(Application)
        .filter(
            Application.status
            == "SUBMITTED"
        )
        .count()
    )

    rejected_applications = (
        db.query(Application)
        .filter(
            Application.status
            == "REJECTED"
        )
        .count()
    )

    # =============================================
    # FEEDBACK STATISTICS
    # =============================================

    total_feedback = (
        db.query(ApplicationFeedback)
        .count()
    )

    interview_count = (
        db.query(ApplicationFeedback)
        .filter(
            ApplicationFeedback.outcome
            == "INTERVIEW"
        )
        .count()
    )

    selected_count = (
        db.query(ApplicationFeedback)
        .filter(
            ApplicationFeedback.outcome
            == "SELECTED"
        )
        .count()
    )

    rejected_count = (
        db.query(ApplicationFeedback)
        .filter(
            ApplicationFeedback.outcome
            == "REJECTED"
        )
        .count()
    )

    no_response_count = (
        db.query(ApplicationFeedback)
        .filter(
            ApplicationFeedback.outcome
            == "NO_RESPONSE"
        )
        .count()
    )

    withdrawn_count = (
        db.query(ApplicationFeedback)
        .filter(
            ApplicationFeedback.outcome
            == "WITHDRAWN"
        )
        .count()
    )

    # =============================================
    # SUCCESS RATE
    # =============================================

    successful_outcomes = (
        interview_count
        + selected_count
    )

    if total_feedback > 0:

        success_rate = (
            successful_outcomes
            / total_feedback
        ) * 100

    else:

        success_rate = 0

    # =============================================
    # INTERVIEW RATE
    # =============================================

    if total_feedback > 0:

        interview_rate = (
            interview_count
            / total_feedback
        ) * 100

    else:

        interview_rate = 0

    # =============================================
    # SELECTION RATE
    # =============================================

    if total_feedback > 0:

        selection_rate = (
            selected_count
            / total_feedback
        ) * 100

    else:

        selection_rate = 0

    # =============================================
    # RETURN ANALYTICS
    # =============================================

    return {
        "success": True,

        "jobs": {
            "total": total_jobs,
            "active": active_jobs,
            "stale": stale_jobs
        },

        "applications": {
            "total": total_applications,
            "pending_approval": (
                pending_approval
            ),
            "approved": (
                approved_applications
            ),
            "submitted": (
                submitted_applications
            ),
            "rejected": (
                rejected_applications
            )
        },

        "feedback": {
            "total": total_feedback,
            "interviews": interview_count,
            "selected": selected_count,
            "rejected": rejected_count,
            "no_response": no_response_count,
            "withdrawn": withdrawn_count
        },

        "performance": {
            "success_rate": round(
                success_rate,
                2
            ),
            "interview_rate": round(
                interview_rate,
                2
            ),
            "selection_rate": round(
                selection_rate,
                2
            )
        }
    }