from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from app.services.learning_ranker import (
    calculate_learning_adjustment
)


def calculate_job_priority(
    job: Dict,
    db: Optional[Session] = None
) -> float:
    """
    Calculate a priority score for a job.

    Higher score means the job should appear
    earlier in the ranked results.

    Learning-based adjustment is optional.
    If no database session is provided, the
    existing ranking behavior is preserved.
    """

    match_score = job.get(
        "match_score",
        0
    )

    salary_min = job.get(
        "salary_min"
    )

    salary_max = job.get(
        "salary_max"
    )

    score = float(match_score)

    # ---------------------------------------------
    # Existing salary priority
    # ---------------------------------------------

    # Give additional priority to jobs
    # where salary information is available.
    if (
        salary_min is not None
        or salary_max is not None
    ):
        score += 5

    # Give additional priority when the
    # maximum salary is available.
    if salary_max is not None:
        score += 5

    # ---------------------------------------------
    # Self-learning adjustment
    # ---------------------------------------------

    learning_adjustment = 0

    learning_result = {
        "adjustment": 0,
        "reason": "LEARNING_NOT_ENABLED"
    }

    if db is not None:

        # Import Job only when learning
        # is actually being used.
        from app.models.job import Job

        job_id = job.get(
            "job_id",
            job.get("id")
        )

        if job_id is not None:

            database_job = (
                db.query(Job)
                .filter(
                    Job.id == job_id
                )
                .first()
            )

            if database_job:

                learning_result = (
                    calculate_learning_adjustment(
                        db=db,
                        job=database_job
                    )
                )

                learning_adjustment = (
                    learning_result.get(
                        "adjustment",
                        0
                    )
                )

                score += learning_adjustment

    # ---------------------------------------------
    # Final score
    # ---------------------------------------------

    return round(
        score,
        2
    )


def rank_jobs(
    jobs: List[Dict],
    db: Optional[Session] = None
) -> List[Dict]:
    """
    Rank jobs from highest priority
    to lowest priority.

    If a database session is provided,
    historical application feedback can
    influence the ranking.
    """

    ranked_jobs = []

    for job in jobs:

        job_copy = dict(job)

        job_copy["priority_score"] = (
            calculate_job_priority(
                job_copy,
                db=db
            )
        )

        ranked_jobs.append(
            job_copy
        )

    ranked_jobs.sort(
        key=lambda job: job[
            "priority_score"
        ],
        reverse=True
    )

    return ranked_jobs