from typing import List, Dict


def calculate_job_priority(job: Dict) -> float:
    """
    Calculate a priority score for a job.

    Higher score means the job should appear
    earlier in the ranked results.
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

    # Give additional priority to jobs
    # where salary information is available.
    if salary_min is not None or salary_max is not None:
        score += 5

    # Give additional priority when the
    # maximum salary is available.
    if salary_max is not None:
        score += 5

    return round(
        score,
        2
    )


def rank_jobs(
    jobs: List[Dict]
) -> List[Dict]:
    """
    Rank jobs from highest priority
    to lowest priority.
    """

    ranked_jobs = []

    for job in jobs:

        job_copy = dict(job)

        job_copy["priority_score"] = (
            calculate_job_priority(
                job_copy
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