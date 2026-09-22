from collections import Counter

from sqlalchemy.orm import Session

from app.models.application_feedback import (
    ApplicationFeedback
)

from app.models.application import (
    Application
)

from app.models.job import Job


SUCCESS_OUTCOMES = {
    "INTERVIEW",
    "SELECTED"
}


def get_learning_summary(
    db: Session
):
    feedback_records = (
        db.query(ApplicationFeedback)
        .order_by(
            ApplicationFeedback.id.asc()
        )
        .all()
    )

    if not feedback_records:

        return {
            "success": True,
            "total_feedback": 0,
            "message": (
                "Not enough feedback data "
                "for learning yet."
            ),
            "outcomes": {},
            "successful_applications": 0,
            "unsuccessful_applications": 0
        }


    # ---------------------------------------------
    # Count outcomes
    # ---------------------------------------------

    outcome_counter = Counter(
        record.outcome
        for record in feedback_records
    )


    successful_count = sum(
        outcome_counter.get(
            outcome,
            0
        )
        for outcome in SUCCESS_OUTCOMES
    )


    unsuccessful_count = (
        len(feedback_records)
        - successful_count
    )


    # ---------------------------------------------
    # Analyze jobs connected to feedback
    # ---------------------------------------------

    successful_jobs = []

    unsuccessful_jobs = []

    for record in feedback_records:

        application = (
            db.query(Application)
            .filter(
                Application.id
                == record.application_id
            )
            .first()
        )

        if not application:
            continue

        job = (
            db.query(Job)
            .filter(
                Job.id
                == application.job_id
            )
            .first()
        )

        if not job:
            continue

        job_data = {
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_type": job.job_type,
            "match_score": job.match_score,
            "priority_score": job.priority_score
        }

        if record.outcome in SUCCESS_OUTCOMES:

            successful_jobs.append(
                job_data
            )

        else:

            unsuccessful_jobs.append(
                job_data
            )


    # ---------------------------------------------
    # Analyze successful job titles
    # ---------------------------------------------

    successful_titles = Counter(
        job["title"]
        for job in successful_jobs
        if job["title"]
    )


    successful_job_types = Counter(
        job["job_type"]
        for job in successful_jobs
        if job["job_type"]
    )


    successful_locations = Counter(
        job["location"]
        for job in successful_jobs
        if job["location"]
    )


    # ---------------------------------------------
    # Calculate average scores
    # ---------------------------------------------

    successful_scores = [
        job["match_score"]
        for job in successful_jobs
        if job["match_score"] is not None
    ]

    unsuccessful_scores = [
        job["match_score"]
        for job in unsuccessful_jobs
        if job["match_score"] is not None
    ]


    successful_average_score = (
        sum(successful_scores)
        / len(successful_scores)
        if successful_scores
        else 0
    )


    unsuccessful_average_score = (
        sum(unsuccessful_scores)
        / len(unsuccessful_scores)
        if unsuccessful_scores
        else 0
    )


    # ---------------------------------------------
    # Return learning summary
    # ---------------------------------------------

    return {
        "success": True,
        "total_feedback": len(
            feedback_records
        ),
        "outcomes": dict(
            outcome_counter
        ),
        "successful_applications": (
            successful_count
        ),
        "unsuccessful_applications": (
            unsuccessful_count
        ),
        "successful_job_titles": dict(
            successful_titles
        ),
        "successful_job_types": dict(
            successful_job_types
        ),
        "successful_locations": dict(
            successful_locations
        ),
        "successful_average_match_score": round(
            successful_average_score,
            2
        ),
        "unsuccessful_average_match_score": round(
            unsuccessful_average_score,
            2
        ),
        "successful_jobs": successful_jobs,
        "unsuccessful_jobs": unsuccessful_jobs
    }