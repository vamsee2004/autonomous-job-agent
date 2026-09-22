from typing import Optional

from sqlalchemy.orm import Session

from app.services.job_source import (
    fetch_jobs
)

from app.services.job_discovery import (
    save_discovered_job
)

from app.models.job import Job


def discover_jobs_from_source(
    db: Session,
    search_title: Optional[str] = None,
    search_location: Optional[str] = None,
    max_pages: Optional[int] = None,
    results_per_page: Optional[int] = None,
    pipeline_run_id=None
):
    """
    Fetch jobs from the configured source
    and process each discovered job.

    pipeline_run_id identifies the automation
    run responsible for discovering the job.
    """

    jobs = fetch_jobs(
        search_title=search_title,
        search_location=search_location,
        max_pages=max_pages,
        results_per_page=results_per_page
    )

    results = []

    saved_count = 0
    duplicate_count = 0
    preference_rejected_count = 0
    score_rejected_count = 0
    salary_rejected_count = 0
    missing_url_count = 0

    for job in jobs:

        result = save_discovered_job(
            db=db,
            title=job["title"],
            company=job["company"],
            location=job["location"],
            description=job["description"],
            source=job["source"],
            url=job["url"],
            salary_min=job.get("salary_min"),
            salary_max=job.get("salary_max"),
            pipeline_run_id=pipeline_run_id
        )

        results.append(result)

        reason = result.get("reason")

        if reason == "ACCEPTED":

            saved_count += 1

        elif reason == "DUPLICATE_REFRESHED":

            duplicate_count += 1

        elif reason == "DUPLICATE":

            duplicate_count += 1

        elif reason == "PREFERENCE_MISMATCH":

            preference_rejected_count += 1

        elif reason == "LOW_MATCH_SCORE":

            score_rejected_count += 1

        elif reason == "SALARY_TOO_LOW":

            salary_rejected_count += 1

        elif reason == "MISSING_URL":

            missing_url_count += 1

    # Get jobs belonging to the current pipeline run.
    if pipeline_run_id is not None:

        ranked_jobs = (
            db.query(Job)
            .filter(
                Job.pipeline_run_id == pipeline_run_id
            )
            .order_by(
                Job.priority_score.desc()
            )
            .all()
        )

    else:

        # Newly discovered jobs are stored as ACTIVE.
        ranked_jobs = (
            db.query(Job)
            .filter(
                Job.status == "ACTIVE"
            )
            .order_by(
                Job.priority_score.desc()
            )
            .all()
        )

    ranked_jobs_response = [
        {
            "job_id": job.id,
            "pipeline_run_id": job.pipeline_run_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "match_score": job.match_score,
            "priority_score": job.priority_score,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "source": job.source,
            "url": job.url,
            "status": job.status,
            "discovered_at": job.discovered_at,
            "last_seen_at": job.last_seen_at
        }
        for job in ranked_jobs
    ]

    return {
        "total_jobs_found": len(jobs),
        "jobs_saved": saved_count,
        "duplicates": duplicate_count,
        "rejected_by_preferences": (
            preference_rejected_count
        ),
        "rejected_by_match_score": (
            score_rejected_count
        ),
        "rejected_by_salary": (
            salary_rejected_count
        ),
        "missing_url": missing_url_count,
        "pipeline_run_id": pipeline_run_id,
        "current_run_job_ids": [
            result["job_id"]
            for result in results
            if (
                result.get("reason") == "ACCEPTED"
                and result.get("job_id")
            )
        ],
        "ranked_jobs": ranked_jobs_response,
        "results": results
    }