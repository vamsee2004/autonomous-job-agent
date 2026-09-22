from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.job import Job


def parse_timestamp(timestamp):
    """
    Convert an ISO timestamp string into datetime.
    """

    if not timestamp:
        return None

    try:
        return datetime.fromisoformat(
            timestamp
        )

    except (ValueError, TypeError):

        return None


def mark_stale_jobs(
    db: Session,
    stale_after_hours: int = 72
):
    """
    Mark jobs as STALE when they have not been
    seen within the configured number of hours.

    Jobs that are already APPLIED or have an
    associated application are not modified here.
    """

    cutoff_time = (
        datetime.now()
        - timedelta(
            hours=stale_after_hours
        )
    )

    jobs = (
        db.query(Job)
        .filter(
            Job.status.in_([
                "ACTIVE",
                "ANALYZED"
            ])
        )
        .all()
    )

    stale_jobs = []

    skipped_jobs = []

    for job in jobs:

        last_seen = parse_timestamp(
            job.last_seen_at
        )

        if last_seen is None:

            skipped_jobs.append({
                "job_id": job.id,
                "reason": (
                    "MISSING_LAST_SEEN_AT"
                )
            })

            continue

        if last_seen < cutoff_time:

            job.status = "STALE"

            stale_jobs.append({
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "last_seen_at": (
                    job.last_seen_at
                ),
                "status": job.status
            })

    db.commit()

    return {
        "success": True,

        "stale_after_hours": (
            stale_after_hours
        ),

        "cutoff_time": (
            cutoff_time.isoformat()
        ),

        "jobs_checked": len(jobs),

        "jobs_marked_stale": (
            len(stale_jobs)
        ),

        "jobs_skipped": (
            len(skipped_jobs)
        ),

        "stale_jobs": stale_jobs,

        "skipped_jobs": skipped_jobs
    }


def get_active_jobs(
    db: Session
):
    """
    Return only currently active jobs.
    """

    return (
        db.query(Job)
        .filter(
            Job.status == "ACTIVE"
        )
        .order_by(
            Job.priority_score.desc()
        )
        .all()
    )


def get_stale_jobs(
    db: Session
):
    """
    Return jobs that have been marked STALE.
    """

    return (
        db.query(Job)
        .filter(
            Job.status == "STALE"
        )
        .order_by(
            Job.last_seen_at.desc()
        )
        .all()
    )