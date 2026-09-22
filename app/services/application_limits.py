import os
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.job import Job

from app.services.portal_permissions import (
    check_portal_permission
)


def get_application_limit_settings():

    try:
        max_applications_per_day = int(
            os.getenv(
                "MAX_APPLICATIONS_PER_DAY",
                "10"
            )
        )
    except ValueError:
        max_applications_per_day = 10

    try:
        max_applications_per_portal = int(
            os.getenv(
                "MAX_APPLICATIONS_PER_PORTAL",
                "5"
            )
        )
    except ValueError:
        max_applications_per_portal = 5

    allowed_job_types = os.getenv(
        "ALLOWED_JOB_TYPES",
        "Full-time,Contract"
    )

    allowed_job_types = [
        job_type.strip().lower()
        for job_type in allowed_job_types.split(",")
        if job_type.strip()
    ]

    return {
        "max_applications_per_day": max(
            max_applications_per_day,
            0
        ),
        "max_applications_per_portal": max(
            max_applications_per_portal,
            0
        ),
        "allowed_job_types": allowed_job_types
    }


def get_today_application_count(
    db: Session
):

    today = datetime.now().date()

    applications = (
        db.query(Application)
        .filter(
            Application.applied_at.isnot(None)
        )
        .all()
    )

    count = 0

    for application in applications:

        if not application.applied_at:
            continue

        try:
            applied_date = (
                datetime.fromisoformat(
                    application.applied_at
                ).date()
            )

        except ValueError:
            continue

        if applied_date == today:
            count += 1

    return count


def get_portal_application_count(
    db: Session,
    portal: str
):

    applications = (
        db.query(Application)
        .join(
            Job,
            Application.job_id == Job.id
        )
        .filter(
            Application.applied_at.isnot(None),
            Job.source == portal
        )
        .all()
    )

    count = 0

    for application in applications:

        if application.applied_at:
            count += 1

    return count


def check_job_type(
    job_type: str,
    allowed_job_types
):

    if not job_type:

        return {
            "allowed": False,
            "reason": "JOB_TYPE_NOT_PROVIDED"
        }

    normalized_job_type = (
        job_type.strip().lower()
    )

    if normalized_job_type not in allowed_job_types:

        return {
            "allowed": False,
            "reason": "JOB_TYPE_NOT_ALLOWED"
        }

    return {
        "allowed": True,
        "reason": "JOB_TYPE_ALLOWED"
    }


def check_application_limits(
    db: Session,
    job: Job
):

    settings = (
        get_application_limit_settings()
    )

    # ---------------------------------
    # 1. Portal permission check
    # ---------------------------------

    portal = job.source or "UNKNOWN"

    portal_check = (
        check_portal_permission(
            portal
        )
    )

    if not portal_check["allowed"]:

        return {
            "allowed": False,
            "reason": portal_check["reason"],
            "message": (
                "Application blocked because "
                "this portal is not enabled"
            ),
            "portal": portal,
            "portal_permission": portal_check
        }

    # ---------------------------------
    # 2. Daily application limit
    # ---------------------------------

    today_count = (
        get_today_application_count(db)
    )

    if (
        today_count
        >= settings["max_applications_per_day"]
    ):

        return {
            "allowed": False,
            "reason": (
                "DAILY_APPLICATION_LIMIT_REACHED"
            ),
            "message": (
                "Maximum daily application "
                "limit has been reached"
            ),
            "today_count": today_count,
            "daily_limit": (
                settings[
                    "max_applications_per_day"
                ]
            ),
            "portal": portal
        }

    # ---------------------------------
    # 3. Portal application limit
    # ---------------------------------

    portal_count = (
        get_portal_application_count(
            db,
            portal
        )
    )

    if (
        portal_count
        >= settings["max_applications_per_portal"]
    ):

        return {
            "allowed": False,
            "reason": (
                "PORTAL_APPLICATION_LIMIT_REACHED"
            ),
            "message": (
                "Maximum application limit "
                "for this portal has been reached"
            ),
            "portal": portal,
            "portal_count": portal_count,
            "portal_limit": (
                settings[
                    "max_applications_per_portal"
                ]
            )
        }

    # ---------------------------------
    # 4. Job type check
    # ---------------------------------

    job_type_result = check_job_type(
        job.job_type,
        settings["allowed_job_types"]
    )

    if not job_type_result["allowed"]:

        return {
            "allowed": False,
            "reason": job_type_result["reason"],
            "message": (
                "Job type is not allowed "
                "for application"
            ),
            "job_type": job.job_type,
            "allowed_job_types": (
                settings["allowed_job_types"]
            ),
            "portal": portal
        }

    # ---------------------------------
    # 5. Everything passed
    # ---------------------------------

    return {
        "allowed": True,
        "reason": (
            "APPLICATION_LIMITS_PASSED"
        ),
        "message": (
            "Application limits passed"
        ),
        "today_count": today_count,
        "daily_limit": (
            settings[
                "max_applications_per_day"
            ]
        ),
        "portal": portal,
        "portal_count": portal_count,
        "portal_limit": (
            settings[
                "max_applications_per_portal"
            ]
        ),
        "job_type": job.job_type,
        "allowed_job_types": (
            settings["allowed_job_types"]
        ),
        "portal_permission": portal_check
    }