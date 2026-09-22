from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.application import Application


def normalize_text(value):
    """
    Normalize text for reliable duplicate comparison.
    """

    if not value:
        return ""

    return " ".join(
        str(value)
        .lower()
        .strip()
        .split()
    )


def normalize_url(value):
    """
    Normalize job URLs so small URL differences
    do not create false duplicates.
    """

    if not value:
        return ""

    url = str(value).strip().lower()

    if url.endswith("/"):
        url = url[:-1]

    return url


def calculate_job_similarity(job1, job2):
    """
    Calculate similarity between two jobs.

    Comparison fields:
    - company
    - title
    - location
    - URL
    """

    company1 = normalize_text(job1.company)
    company2 = normalize_text(job2.company)

    title1 = normalize_text(job1.title)
    title2 = normalize_text(job2.title)

    location1 = normalize_text(job1.location)
    location2 = normalize_text(job2.location)

    url1 = normalize_url(job1.url)
    url2 = normalize_url(job2.url)

    score = 0

    if company1 and company1 == company2:
        score += 40

    if title1 and title1 == title2:
        score += 30

    if location1 and location1 == location2:
        score += 10

    if url1 and url2 and url1 == url2:
        score += 20

    return score


def find_duplicate_job(
    db: Session,
    job: Job
):
    """
    Find an existing job that represents the same
    opportunity as the supplied job.

    Returns:
        duplicate Job object
        or None
    """

    jobs = (
        db.query(Job)
        .filter(Job.id != job.id)
        .all()
    )

    for existing_job in jobs:

        # Exact URL match is a strong duplicate signal.
        if (
            normalize_url(job.url)
            and normalize_url(existing_job.url)
            and normalize_url(job.url)
            == normalize_url(existing_job.url)
        ):
            return existing_job

        similarity = calculate_job_similarity(
            job,
            existing_job
        )

        # Company + title + location
        # gives a strong duplicate match.
        if similarity >= 80:
            return existing_job

    return None


def find_application_duplicate(
    db: Session,
    job: Job
):
    """
    Check whether an application already exists
    for the supplied job or an equivalent job.
    """

    # First check direct job ID.
    existing_application = (
        db.query(Application)
        .filter(
            Application.job_id == job.id
        )
        .first()
    )

    if existing_application:
        return {
            "is_duplicate": True,
            "reason": "APPLICATION_ALREADY_EXISTS",
            "application_id": existing_application.id,
            "job_id": job.id
        }

    # Then check equivalent jobs.
    duplicate_job = find_duplicate_job(
        db,
        job
    )

    if not duplicate_job:
        return {
            "is_duplicate": False,
            "reason": "NO_DUPLICATE"
        }

    duplicate_application = (
        db.query(Application)
        .filter(
            Application.job_id
            == duplicate_job.id
        )
        .first()
    )

    if duplicate_application:
        return {
            "is_duplicate": True,
            "reason": "CROSS_PORTAL_DUPLICATE",
            "application_id": duplicate_application.id,
            "job_id": duplicate_job.id,
            "duplicate_job_id": duplicate_job.id,
            "duplicate_job_title": duplicate_job.title,
            "duplicate_job_company": duplicate_job.company,
            "duplicate_job_source": duplicate_job.source
        }

    return {
        "is_duplicate": False,
        "reason": "SIMILAR_JOB_WITHOUT_APPLICATION",
        "duplicate_job_id": duplicate_job.id
    }


def check_cross_portal_duplicate(
    db: Session,
    job: Job
):
    """
    Public function used by the application workflow.
    """

    result = find_application_duplicate(
        db,
        job
    )

    return result