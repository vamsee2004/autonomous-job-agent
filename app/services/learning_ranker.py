from collections import Counter

from sqlalchemy.orm import Session

from app.models.application_feedback import (
    ApplicationFeedback
)

from app.models.application import (
    Application
)

from app.models.job import Job


# Learning will not affect ranking until
# enough historical feedback exists.
MINIMUM_FEEDBACK_RECORDS = 5


SUCCESS_OUTCOMES = {
    "INTERVIEW",
    "SELECTED"
}


FAILURE_OUTCOMES = {
    "REJECTED",
    "NO_RESPONSE"
}


def calculate_learning_adjustment(
    db: Session,
    job: Job
):
    """
    Calculate a small ranking adjustment based
    on historical application outcomes.

    The adjustment is intentionally limited so
    historical feedback cannot completely
    override the existing ranking system.
    """

    feedback_records = (
        db.query(ApplicationFeedback)
        .all()
    )

    if len(feedback_records) < MINIMUM_FEEDBACK_RECORDS:

        return {
            "adjustment": 0,
            "reason": "INSUFFICIENT_FEEDBACK",
            "feedback_count": len(
                feedback_records
            )
        }

    successful_jobs = []

    unsuccessful_jobs = []

    for feedback in feedback_records:

        application = (
            db.query(Application)
            .filter(
                Application.id
                == feedback.application_id
            )
            .first()
        )

        if not application:
            continue

        historical_job = (
            db.query(Job)
            .filter(
                Job.id
                == application.job_id
            )
            .first()
        )

        if not historical_job:
            continue

        if feedback.outcome in SUCCESS_OUTCOMES:

            successful_jobs.append(
                historical_job
            )

        elif feedback.outcome in FAILURE_OUTCOMES:

            unsuccessful_jobs.append(
                historical_job
            )

    adjustment = 0

    # ---------------------------------------------
    # Job title learning
    # ---------------------------------------------

    successful_titles = Counter(
        normalize_text(job_item.title)
        for job_item in successful_jobs
        if job_item.title
    )

    unsuccessful_titles = Counter(
        normalize_text(job_item.title)
        for job_item in unsuccessful_jobs
        if job_item.title
    )

    current_title = normalize_text(
        job.title
    )

    if current_title:

        if successful_titles.get(
            current_title,
            0
        ) > 0:

            adjustment += 5

        if unsuccessful_titles.get(
            current_title,
            0
        ) > 0:

            adjustment -= 3

    # ---------------------------------------------
    # Location learning
    # ---------------------------------------------

    successful_locations = Counter(
        normalize_text(job_item.location)
        for job_item in successful_jobs
        if job_item.location
    )

    current_location = normalize_text(
        job.location
    )

    if current_location:

        if successful_locations.get(
            current_location,
            0
        ) > 0:

            adjustment += 3

    # ---------------------------------------------
    # Job type learning
    # ---------------------------------------------

    successful_job_types = Counter(
        normalize_text(job_item.job_type)
        for job_item in successful_jobs
        if job_item.job_type
    )

    current_job_type = normalize_text(
        job.job_type
    )

    if current_job_type:

        if successful_job_types.get(
            current_job_type,
            0
        ) > 0:

            adjustment += 2

    # ---------------------------------------------
    # Safety limit
    # ---------------------------------------------

    adjustment = max(
        -10,
        min(
            adjustment,
            10
        )
    )

    return {
        "adjustment": adjustment,
        "reason": "LEARNING_APPLIED",
        "feedback_count": len(
            feedback_records
        ),
        "successful_jobs": len(
            successful_jobs
        ),
        "unsuccessful_jobs": len(
            unsuccessful_jobs
        )
    }


def normalize_text(value):

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
    )