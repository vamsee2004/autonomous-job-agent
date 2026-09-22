import json

from pathlib import Path
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.job import Job

from app.services.jd_analyzer import (
    analyze_job_description
)

from app.services.job_matcher import (
    calculate_match
)

from app.services.job_ranker import (
    calculate_job_priority
)

from app.services.logger import logger


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


PROFILE_PATH = (
    PROJECT_ROOT
    / "app"
    / "knowledge"
    / "candidate_profile.json"
)


def get_current_timestamp():
    """
    Return the current timestamp in ISO format.
    """

    return datetime.now().isoformat()


def job_matches_preferences(
    candidate,
    title,
    location,
    description
):
    preferences = candidate.get(
        "preferences",
        {}
    )

    preferred_titles = [
        preferred_title.lower()
        for preferred_title in preferences.get(
            "job_titles",
            []
        )
    ]

    preferred_locations = [
        preferred_location.lower()
        for preferred_location in preferences.get(
            "locations",
            []
        )
    ]

    title_matches = True

    if preferred_titles:

        title_matches = any(
            preferred_title in title.lower()
            for preferred_title in preferred_titles
        )

    location_matches = True

    if preferred_locations:

        location_matches = any(
            preferred_location in location.lower()
            for preferred_location in preferred_locations
        )

    return {
        "title_matches": title_matches,

        "location_matches": location_matches,

        "matches_preferences": (
            title_matches
            and location_matches
        )
    }


def save_discovered_job(
    db: Session,
    title: str,
    company: str,
    location: str,
    description: str,
    source: str,
    url: str,
    salary_min=None,
    salary_max=None,
    pipeline_run_id=None
):
    """
    Save and analyze a discovered job.

    Processing includes:

    1. URL validation
    2. Duplicate checking
    3. Duplicate refresh
    4. Preference filtering
    5. JD analysis
    6. Skill matching
    7. Salary filtering
    8. Priority calculation
    9. Database storage
    10. Pipeline run tracking
    """

    logger.info(
        f"Processing discovered job: "
        f"title='{title}', "
        f"company='{company}', "
        f"location='{location}'"
    )

    if not url:

        logger.warning(
            f"Job rejected because URL is missing: "
            f"title='{title}', "
            f"company='{company}'"
        )

        return {
            "success": False,
            "saved": False,
            "duplicate": False,
            "reason": "MISSING_URL",
            "message": "Job URL is missing"
        }

    current_timestamp = (
        get_current_timestamp()
    )

    existing_job = (
        db.query(Job)
        .filter(
            Job.url == url
        )
        .first()
    )

    if existing_job:

        original_status = (
            existing_job.status
        )

        existing_job.last_seen_at = (
            current_timestamp
        )

        if existing_job.status == "STALE":

            existing_job.status = "ACTIVE"

            logger.info(
                f"Stale job reactivated: "
                f"job_id={existing_job.id}, "
                f"title='{existing_job.title}', "
                f"company='{existing_job.company}'"
            )

        if pipeline_run_id is not None:

            existing_job.pipeline_run_id = (
                pipeline_run_id
            )

        db.commit()

        db.refresh(existing_job)

        logger.info(
            f"Duplicate job refreshed: "
            f"job_id={existing_job.id}, "
            f"title='{existing_job.title}', "
            f"company='{existing_job.company}'"
        )

        return {
            "success": True,
            "saved": False,
            "duplicate": True,
            "reactivated": (
                original_status == "STALE"
            ),
            "reason": "DUPLICATE_REFRESHED",
            "message": (
                "Job already exists; "
                "last_seen_at updated"
            ),
            "job_id": existing_job.id,
            "pipeline_run_id": (
                existing_job.pipeline_run_id
            ),
            "title": existing_job.title,
            "company": existing_job.company,
            "location": existing_job.location,
            "match_score": (
                existing_job.match_score
            ),
            "priority_score": (
                existing_job.priority_score
            ),
            "status": existing_job.status,
            "discovered_at": (
                existing_job.discovered_at
            ),
            "last_seen_at": (
                existing_job.last_seen_at
            )
        }

    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        candidate = json.load(file)

    preferences = candidate.get(
        "preferences",
        {}
    )

    preference_check = (
        job_matches_preferences(
            candidate,
            title,
            location,
            description
        )
    )

    if not preference_check[
        "matches_preferences"
    ]:

        logger.info(
            f"Job rejected by preferences: "
            f"title='{title}', "
            f"company='{company}', "
            f"title_matches="
            f"{preference_check['title_matches']}, "
            f"location_matches="
            f"{preference_check['location_matches']}"
        )

        return {
            "success": False,
            "saved": False,
            "duplicate": False,
            "reason": "PREFERENCE_MISMATCH",
            "message": (
                "Job does not match "
                "candidate preferences"
            ),
            "preference_check": (
                preference_check
            )
        }

    analysis = (
        analyze_job_description(
            description
        )
    )

    candidate_skills = candidate.get(
        "skills",
        []
    )

    match = calculate_match(
        candidate_skills,
        analysis["skills"]
    )

    minimum_match_score = (
        preferences.get(
            "minimum_match_score",
            50
        )
    )

    if match["score"] < minimum_match_score:

        logger.info(
            f"Job rejected by match score: "
            f"title='{title}', "
            f"company='{company}', "
            f"score={match['score']}, "
            f"minimum={minimum_match_score}"
        )

        return {
            "success": False,
            "saved": False,
            "duplicate": False,
            "reason": "LOW_MATCH_SCORE",
            "message": (
                "Job match score is below "
                "minimum requirement"
            ),
            "match_score": match["score"],
            "minimum_match_score": (
                minimum_match_score
            ),
            "match": match
        }

    minimum_salary = preferences.get(
        "minimum_salary",
        0
    )

    salary_check = "NOT_REQUIRED"

    if minimum_salary > 0:

        if salary_max is None:

            salary_check = (
                "SALARY_NOT_PROVIDED"
            )

            logger.info(
                f"Salary not provided: "
                f"title='{title}', "
                f"company='{company}'"
            )

        elif salary_max < minimum_salary:

            logger.info(
                f"Job rejected by salary: "
                f"title='{title}', "
                f"company='{company}', "
                f"salary_max={salary_max}, "
                f"minimum={minimum_salary}"
            )

            return {
                "success": False,
                "saved": False,
                "duplicate": False,
                "reason": "SALARY_TOO_LOW",
                "message": (
                    "Job salary is below "
                    "minimum salary requirement"
                ),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "minimum_salary": (
                    minimum_salary
                )
            }

        else:

            salary_check = "PASSED"

            logger.info(
                f"Salary requirement passed: "
                f"title='{title}', "
                f"company='{company}', "
                f"salary_max={salary_max}"
            )

    priority_score = (
        calculate_job_priority(
            {
                "match_score": (
                    match["score"]
                ),
                "salary_min": (
                    salary_min
                ),
                "salary_max": (
                    salary_max
                )
            }
        )
    )

    new_job = Job(
        pipeline_run_id=(
            pipeline_run_id
        ),
        title=title,
        company=company,
        location=location,
        description=description,
        source=source,
        url=url,
        salary_min=salary_min,
        salary_max=salary_max,
        match_score=int(
            match["score"]
        ),
        priority_score=int(
            priority_score
        ),
        status="ACTIVE",
        discovered_at=(
            current_timestamp
        ),
        last_seen_at=(
            current_timestamp
        )
    )

    db.add(new_job)

    db.commit()

    db.refresh(new_job)

    logger.info(
        f"Job accepted and saved: "
        f"job_id={new_job.id}, "
        f"title='{new_job.title}', "
        f"company='{new_job.company}', "
        f"match_score={new_job.match_score}, "
        f"priority_score={new_job.priority_score}, "
        f"salary_check={salary_check}"
    )

    return {
        "success": True,
        "saved": True,
        "duplicate": False,
        "reason": "ACCEPTED",
        "message": (
            "New job discovered, analyzed "
            "and saved"
        ),
        "job_id": new_job.id,
        "pipeline_run_id": (
            new_job.pipeline_run_id
        ),
        "title": new_job.title,
        "company": new_job.company,
        "location": new_job.location,
        "salary_min": (
            new_job.salary_min
        ),
        "salary_max": (
            new_job.salary_max
        ),
        "match_score": (
            new_job.match_score
        ),
        "priority_score": (
            new_job.priority_score
        ),
        "discovered_at": (
            new_job.discovered_at
        ),
        "last_seen_at": (
            new_job.last_seen_at
        ),
        "preference_check": (
            preference_check
        ),
        "analysis": analysis,
        "match": match,
        "minimum_match_score": (
            minimum_match_score
        ),
        "minimum_salary": (
            minimum_salary
        ),
        "salary_check": salary_check,
        "status": new_job.status
    }