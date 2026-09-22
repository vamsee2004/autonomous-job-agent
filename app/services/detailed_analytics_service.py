from collections import Counter

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.application_feedback import (
    ApplicationFeedback
)
from app.models.job import Job


SUCCESS_OUTCOMES = {
    "INTERVIEW",
    "SELECTED"
}


def get_detailed_analytics(
    db: Session
):
    feedback_records = (
        db.query(ApplicationFeedback)
        .order_by(
            ApplicationFeedback.id.asc()
        )
        .all()
    )

    title_outcomes = Counter()
    company_outcomes = Counter()
    location_outcomes = Counter()
    source_outcomes = Counter()

    successful_titles = Counter()
    successful_companies = Counter()
    successful_locations = Counter()
    successful_sources = Counter()

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

        title = (
            job.title
            or "Unknown"
        )

        company = (
            job.company
            or "Unknown"
        )

        location = (
            job.location
            or "Unknown"
        )

        source = (
            job.source
            or "Unknown"
        )

        title_outcomes[
            f"{title} | {feedback.outcome}"
        ] += 1

        company_outcomes[
            f"{company} | {feedback.outcome}"
        ] += 1

        location_outcomes[
            f"{location} | {feedback.outcome}"
        ] += 1

        source_outcomes[
            f"{source} | {feedback.outcome}"
        ] += 1

        if feedback.outcome in SUCCESS_OUTCOMES:

            successful_titles[
                title
            ] += 1

            successful_companies[
                company
            ] += 1

            successful_locations[
                location
            ] += 1

            successful_sources[
                source
            ] += 1

    return {
        "success": True,

        "feedback_records": len(
            feedback_records
        ),

        "outcomes_by_job_title": dict(
            title_outcomes
        ),

        "outcomes_by_company": dict(
            company_outcomes
        ),

        "outcomes_by_location": dict(
            location_outcomes
        ),

        "outcomes_by_source": dict(
            source_outcomes
        ),

        "successful_job_titles": dict(
            successful_titles
        ),

        "successful_companies": dict(
            successful_companies
        ),

        "successful_locations": dict(
            successful_locations
        ),

        "successful_sources": dict(
            successful_sources
        )
    }