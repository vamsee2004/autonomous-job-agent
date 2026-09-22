import json
import os

from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from sqlalchemy.orm import Session

from app.services.jd_analyzer import (
    analyze_job_description
)

from app.services.job_matcher import (
    calculate_match
)

from app.services.job_resume_service import (
    generate_resume_for_job,
    generate_application_documents
)

from app.services.job_discovery import (
    save_discovered_job
)

from app.services.job_search_service import (
    discover_jobs_from_source
)

from app.services.automated_job_pipeline import (
    run_job_search_pipeline
)

from app.services.scheduler import (
    get_scheduler_settings,
    scheduler,
    run_scheduled_job_search
)

from app.services.job_lifecycle import (
    mark_stale_jobs,
    get_active_jobs,
    get_stale_jobs
)

from app.database.connection import SessionLocal

from app.models.job import Job

from app.models.application import Application

from app.models.pipeline_run import PipelineRun


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


PROFILE_PATH = (
    PROJECT_ROOT
    / "app"
    / "knowledge"
    / "candidate_profile.json"
)


class JobDescription(BaseModel):

    title: str

    company: str

    location: str

    description: str

    source: str = "Manual"

    url: str = ""

    salary_min: int | None = None

    salary_max: int | None = None


class JobSearchRequest(BaseModel):

    search_title: str = "Java Developer"

    search_location: str = "Hyderabad"

    max_pages: int = 1

    results_per_page: int = 20


class RankedJobRequest(BaseModel):

    minimum_priority_score: int = 0


class ApplicationStatusRequest(BaseModel):

    status: str

    notes: str | None = None


def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ============================================================
# JOB ANALYSIS
# ============================================================


@router.post("/analyze")
def analyze_job(
    job: JobDescription,
    db: Session = Depends(get_db)
):

    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        candidate = json.load(file)

    analysis = analyze_job_description(
        job.description
    )

    candidate_skills = candidate.get(
        "skills",
        []
    )

    match = calculate_match(
        candidate_skills,
        analysis["skills"]
    )

    current_timestamp = (
        datetime.now().isoformat()
    )

    database_job = Job(
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        source=job.source,
        url=job.url,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        match_score=int(
            match["score"]
        ),
        status="ACTIVE",
        discovered_at=current_timestamp,
        last_seen_at=current_timestamp
    )

    db.add(database_job)

    db.commit()

    db.refresh(database_job)

    return {
        "message": (
            "Job analyzed and saved"
        ),

        "job_id": database_job.id,

        "pipeline_run_id": (
            database_job.pipeline_run_id
        ),

        "status": database_job.status,

        "discovered_at": (
            database_job.discovered_at
        ),

        "last_seen_at": (
            database_job.last_seen_at
        ),

        "analysis": analysis,

        "match": match,

        "salary_min": (
            database_job.salary_min
        ),

        "salary_max": (
            database_job.salary_max
        )
    }


# ============================================================
# GET ALL JOBS
# ============================================================


@router.get("/")
def get_jobs(
    db: Session = Depends(get_db)
):

    jobs = (
        db.query(Job)
        .all()
    )

    return [
        {
            "job_id": job.id,

            "pipeline_run_id": (
                job.pipeline_run_id
            ),

            "title": job.title,

            "company": job.company,

            "location": job.location,

            "description": job.description,

            "source": job.source,

            "url": job.url,

            "salary_min": job.salary_min,

            "salary_max": job.salary_max,

            "match_score": job.match_score,

            "priority_score": (
                job.priority_score
            ),

            "status": job.status,

            "discovered_at": (
                job.discovered_at
            ),

            "last_seen_at": (
                job.last_seen_at
            )
        }
        for job in jobs
    ]


# ============================================================
# RANKED JOBS
# ============================================================


@router.post("/ranked")
def get_ranked_jobs(
    request: RankedJobRequest,
    db: Session = Depends(get_db)
):

    jobs = (
        db.query(Job)
        .filter(
            Job.priority_score >= (
                request.minimum_priority_score
            )
        )
        .order_by(
            Job.priority_score.desc()
        )
        .all()
    )

    return {
        "minimum_priority_score": (
            request.minimum_priority_score
        ),

        "total_jobs": len(jobs),

        "jobs": [
            {
                "job_id": job.id,

                "pipeline_run_id": (
                    job.pipeline_run_id
                ),

                "title": job.title,

                "company": job.company,

                "location": job.location,

                "match_score": (
                    job.match_score
                ),

                "priority_score": (
                    job.priority_score
                ),

                "salary_min": (
                    job.salary_min
                ),

                "salary_max": (
                    job.salary_max
                ),

                "source": job.source,

                "url": job.url,

                "status": job.status,

                "discovered_at": (
                    job.discovered_at
                ),

                "last_seen_at": (
                    job.last_seen_at
                )
            }
            for job in jobs
        ]
    }


# ============================================================
# RESUME GENERATION
# ============================================================


@router.post(
    "/{job_id}/generate-resume"
)
def generate_job_resume_api(
    job_id: int,
    db: Session = Depends(get_db)
):

    return generate_resume_for_job(
        db,
        job_id
    )


# ============================================================
# APPLICATION PREPARATION
# ============================================================


@router.post(
    "/{job_id}/prepare-application"
)
def prepare_application_api(
    job_id: int,
    db: Session = Depends(get_db)
):

    return generate_application_documents(
        db,
        job_id
    )


# ============================================================
# APPLICATIONS
# ============================================================


@router.get("/applications")
def get_applications(
    db: Session = Depends(get_db)
):

    applications = (
        db.query(Application)
        .all()
    )

    return [
        {
            "application_id": application.id,

            "pipeline_run_id": (
                application.pipeline_run_id
            ),

            "job_id": application.job_id,

            "status": application.status,

            "mode": application.mode,

            "approval_required": (
                application.approval_required
            ),

            "approved": application.approved,

            "resume_file": (
                application.resume_file
            ),

            "cover_letter_file": (
                application.cover_letter_file
            ),

            "applied_at": (
                application.applied_at
            ),

            "notes": application.notes
        }
        for application in applications
    ]


# ============================================================
# PENDING APPROVAL
# ============================================================


@router.get(
    "/applications/pending-approval"
)
def get_pending_approval_applications(
    db: Session = Depends(get_db)
):

    # __define-ocg__

    varOcg = (
        db.query(Application)
        .filter(
            Application.status == "PREPARED",

            Application.mode
            == "APPROVAL_REQUIRED",

            Application.approval_required
            == 1,

            Application.approved
            == 0
        )
        .all()
    )

    return {
        "success": True,

        "total_pending": len(
            varOcg
        ),

        "approval_required": True,

        "applications": [
            {
                "application_id": application.id,

                "pipeline_run_id": (
                    application.pipeline_run_id
                ),

                "job_id": application.job_id,

                "status": application.status,

                "mode": application.mode,

                "approval_required": (
                    application.approval_required
                ),

                "approved": application.approved,

                "resume_file": (
                    application.resume_file
                ),

                "cover_letter_file": (
                    application.cover_letter_file
                ),

                "notes": application.notes
            }
            for application in varOcg
        ]
    }


# ============================================================
# APPLICATION REVIEW
# ============================================================


@router.get(
    "/applications/{application_id}/review"
)
def review_application(
    application_id: int,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if application is None:

        return {
            "success": False,
            "message": (
                "Application not found"
            )
        }

    job = (
        db.query(Job)
        .filter(
            Job.id == application.job_id
        )
        .first()
    )

    if job is None:

        return {
            "success": False,
            "message": (
                "Associated job not found"
            )
        }

    resume_exists = False

    if application.resume_file:

        resume_exists = Path(
            application.resume_file
        ).exists()

    cover_letter_exists = False

    if application.cover_letter_file:

        cover_letter_exists = Path(
            application.cover_letter_file
        ).exists()

    return {
        "success": True,

        "application": {
            "application_id": application.id,

            "pipeline_run_id": (
                application.pipeline_run_id
            ),

            "status": application.status,

            "mode": application.mode,

            "approval_required": (
                application.approval_required
            ),

            "approved": application.approved,

            "applied_at": (
                application.applied_at
            )
        },

        "job": {
            "job_id": job.id,

            "pipeline_run_id": (
                job.pipeline_run_id
            ),

            "title": job.title,

            "company": job.company,

            "location": job.location,

            "source": job.source,

            "url": job.url,

            "salary_min": job.salary_min,

            "salary_max": job.salary_max,

            "match_score": job.match_score,

            "priority_score": (
                job.priority_score
            ),

            "status": job.status,

            "description": job.description,

            "discovered_at": (
                job.discovered_at
            ),

            "last_seen_at": (
                job.last_seen_at
            )
        },

        "documents": {
            "resume_file": (
                application.resume_file
            ),

            "resume_exists": resume_exists,

            "cover_letter_file": (
                application.cover_letter_file
            ),

            "cover_letter_exists": (
                cover_letter_exists
            )
        },

        "approval": {
            "required": True,

            "currently_approved": (
                application.approved == 1
            ),

            "can_approve": (
                application.status
                in [
                    "PREPARED",
                    "READY"
                ]
                and application.approved == 0
            ),

            "can_submit": (
                application.status
                == "APPROVED"
                and application.approved == 1
            )
        }
    }


# ============================================================
# GET SINGLE APPLICATION
# ============================================================


@router.get(
    "/applications/{application_id}"
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if application is None:

        return {
            "success": False,
            "message": (
                "Application not found"
            )
        }

    return {
        "application_id": application.id,

        "pipeline_run_id": (
            application.pipeline_run_id
        ),

        "job_id": application.job_id,

        "status": application.status,

        "mode": application.mode,

        "approval_required": (
            application.approval_required
        ),

        "approved": application.approved,

        "resume_file": (
            application.resume_file
        ),

        "cover_letter_file": (
            application.cover_letter_file
        ),

        "applied_at": (
            application.applied_at
        ),

        "notes": application.notes
    }


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================


@router.put(
    "/applications/{application_id}/status"
)
def update_application_status(
    application_id: int,
    request: ApplicationStatusRequest,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if application is None:

        return {
            "success": False,
            "message": (
                "Application not found"
            )
        }

    allowed_statuses = [
        "PREPARED",
        "READY",
        "APPROVED",
        "APPLIED",
        "ASSESSMENT",
        "INTERVIEW",
        "REJECTED",
        "OFFER"
    ]

    if request.status not in allowed_statuses:

        return {
            "success": False,

            "message": (
                "Invalid application status"
            ),

            "allowed_statuses": (
                allowed_statuses
            )
        }

    if (
        request.status == "APPLIED"
        and application.approved != 1
    ):

        return {
            "success": False,

            "message": (
                "Application must be approved "
                "before it can be marked as APPLIED"
            ),

            "current_status": (
                application.status
            ),

            "approved": (
                application.approved
            )
        }

    application.status = (
        request.status
    )

    if request.notes is not None:

        application.notes = (
            request.notes
        )

    if request.status == "APPLIED":

        application.applied_at = (
            datetime.now().isoformat()
        )

    db.commit()

    db.refresh(application)

    return {
        "success": True,

        "application_id": application.id,

        "pipeline_run_id": (
            application.pipeline_run_id
        ),

        "status": application.status,

        "mode": application.mode,

        "approved": application.approved,

        "applied_at": (
            application.applied_at
        ),

        "notes": application.notes
    }


# ============================================================
# MARK APPLICATION READY
# ============================================================


@router.put(
    "/applications/{application_id}/ready"
)
def mark_application_ready(
    application_id: int,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if application is None:

        return {
            "success": False,
            "message": (
                "Application not found"
            )
        }

    if application.status != "PREPARED":

        return {
            "success": False,

            "message": (
                "Only PREPARED applications "
                "can be marked as READY"
            ),

            "current_status": (
                application.status
            )
        }

    application.status = "READY"

    if application.notes:

        application.notes += (
            " Application is ready for approval."
        )

    else:

        application.notes = (
            "Application is ready for approval."
        )

    db.commit()

    db.refresh(application)

    return {
        "success": True,

        "message": (
            "Application marked as READY"
        ),

        "application_id": application.id,

        "pipeline_run_id": (
            application.pipeline_run_id
        ),

        "status": application.status,

        "mode": application.mode,

        "approval_required": (
            application.approval_required
        ),

        "approved": application.approved
    }


# ============================================================
# APPROVE APPLICATION
# ============================================================


@router.put(
    "/applications/{application_id}/approve"
)
def approve_application(
    application_id: int,
    db: Session = Depends(get_db)
):

    application = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if application is None:

        return {
            "success": False,
            "message": (
                "Application not found"
            )
        }

    if application.mode != "APPROVAL_REQUIRED":

        return {
            "success": False,

            "message": (
                "Application approval mode is "
                "not configured correctly"
            ),

            "mode": application.mode
        }

    if application.approval_required != 1:

        return {
            "success": False,

            "message": (
                "This application does not "
                "require approval"
            )
        }

    if application.status not in [
        "PREPARED",
        "READY"
    ]:

        return {
            "success": False,

            "message": (
                "Application cannot be approved "
                "from its current status"
            ),

            "current_status": (
                application.status
            )
        }

    application.approved = 1

    application.status = "APPROVED"

    if application.notes:

        application.notes += (
            " Application approved."
        )

    else:

        application.notes = (
            "Application approved."
        )

    db.commit()

    db.refresh(application)

    return {
        "success": True,

        "message": (
            "Application approved successfully"
        ),

        "application_id": application.id,

        "pipeline_run_id": (
            application.pipeline_run_id
        ),

        "status": application.status,

        "mode": application.mode,

        "approved": application.approved
    }


# ============================================================
# SUBMIT APPLICATION
# ============================================================


@router.post(
    "/applications/{application_id}/submit"
)
def submit_application(
    application_id: int,
    db: Session = Depends(get_db)
):

    # __define-pcb__

    varPcb = (
        db.query(Application)
        .filter(
            Application.id == application_id
        )
        .first()
    )

    if varPcb is None:

        return {
            "success": False,
            "message": (
                "Application not found"
            )
        }

    if varPcb.mode != "APPROVAL_REQUIRED":

        return {
            "success": False,

            "message": (
                "Application mode is not "
                "configured for approved submission"
            ),

            "mode": varPcb.mode
        }

    if varPcb.approval_required != 1:

        return {
            "success": False,

            "message": (
                "Application approval is required"
            )
        }

    if varPcb.approved != 1:

        return {
            "success": False,

            "message": (
                "Application must be approved "
                "before submission"
            ),

            "approved": varPcb.approved
        }

    if varPcb.status != "APPROVED":

        return {
            "success": False,

            "message": (
                "Only APPROVED applications "
                "can be submitted"
            ),

            "current_status": (
                varPcb.status
            )
        }

    varPcb.status = "APPLIED"

    varPcb.applied_at = (
        datetime.now().isoformat()
    )

    if varPcb.notes:

        varPcb.notes += (
            " Application submitted."
        )

    else:

        varPcb.notes = (
            "Application submitted."
        )

    db.commit()

    db.refresh(varPcb)

    return {
        "success": True,

        "message": (
            "Application marked as submitted"
        ),

        "application_id": varPcb.id,

        "pipeline_run_id": (
            varPcb.pipeline_run_id
        ),

        "job_id": varPcb.job_id,

        "status": varPcb.status,

        "mode": varPcb.mode,

        "approved": varPcb.approved,

        "applied_at": varPcb.applied_at
    }


# ============================================================
# MANUAL JOB DISCOVERY
# ============================================================


@router.post("/discover")
def discover_job(
    job: JobDescription,
    db: Session = Depends(get_db)
):

    return save_discovered_job(
        db=db,

        title=job.title,

        company=job.company,

        location=job.location,

        description=job.description,

        source=job.source,

        url=job.url,

        salary_min=job.salary_min,

        salary_max=job.salary_max
    )


# ============================================================
# JOB SEARCH
# ============================================================


@router.post("/search")
def search_jobs(
    request: JobSearchRequest,
    db: Session = Depends(get_db)
):

    search_result = (
        discover_jobs_from_source(
            db=db,

            search_title=(
                request.search_title
            ),

            search_location=(
                request.search_location
            ),

            max_pages=(
                request.max_pages
            ),

            results_per_page=(
                request.results_per_page
            )
        )
    )

    return {
        "message": (
            "Job search completed"
        ),

        "search_title": (
            request.search_title
        ),

        "search_location": (
            request.search_location
        ),

        "total_jobs_found": (
            search_result[
                "total_jobs_found"
            ]
        ),

        "jobs_saved": (
            search_result[
                "jobs_saved"
            ]
        ),

        "duplicates": (
            search_result[
                "duplicates"
            ]
        ),

        "rejected_by_preferences": (
            search_result[
                "rejected_by_preferences"
            ]
        ),

        "rejected_by_match_score": (
            search_result[
                "rejected_by_match_score"
            ]
        ),

        "rejected_by_salary": (
            search_result[
                "rejected_by_salary"
            ]
        ),

        "missing_url": (
            search_result[
                "missing_url"
            ]
        ),

        "ranked_jobs": (
            search_result[
                "ranked_jobs"
            ]
        )
    }


# ============================================================
# AUTOMATED SEARCH
# ============================================================


@router.post("/automated-search")
def automated_search(
    request: JobSearchRequest,
    db: Session = Depends(get_db)
):

    return run_job_search_pipeline(
        db=db,

        search_title=(
            request.search_title
        ),

        search_location=(
            request.search_location
        ),

        max_pages=(
            request.max_pages
        ),

        results_per_page=(
            request.results_per_page
        )
    )


# ============================================================
# RUN COMPLETE PIPELINE NOW
# ============================================================


@router.post("/search/run-now")
def run_search_now():

    db = SessionLocal()

    try:

        result = run_job_search_pipeline(
            db=db
        )

        return result

    finally:

        db.close()


# ============================================================
# SCHEDULER STATUS
# ============================================================


@router.get("/scheduler/status")
def get_scheduler_status():

    settings = (
        get_scheduler_settings()
    )

    jobs = scheduler.get_jobs()

    next_run_time = None

    if jobs:

        next_run_time = (
            jobs[0].next_run_time.isoformat()
            if jobs[0].next_run_time
            else None
        )

    return {
        "success": True,

        "scheduler_running": (
            scheduler.running
        ),

        "search_title": (
            settings["search_title"]
        ),

        "search_location": (
            settings["search_location"]
        ),

        "interval_hours": (
            settings["interval_hours"]
        ),

        "max_pages": (
            settings["max_pages"]
        ),

        "results_per_page": (
            settings["results_per_page"]
        ),

        "next_run_time": (
            next_run_time
        )
    }


# ============================================================
# RUN SCHEDULER NOW
# ============================================================


@router.post("/scheduler/run-now")
def run_scheduler_now():

    run_scheduled_job_search()

    return {
        "success": True,

        "message": (
            "Scheduled job-search pipeline "
            "was triggered successfully"
        ),

        "approval_required": True
    }


# ============================================================
# JOB LIFECYCLE
# ============================================================


@router.post("/lifecycle/cleanup")
def cleanup_stale_jobs(
    db: Session = Depends(get_db)
):

    try:

        stale_after_hours = int(
            os.getenv(
                "JOB_STALE_AFTER_HOURS",
                "72"
            )
        )

    except ValueError:

        stale_after_hours = 72

    return mark_stale_jobs(
        db=db,

        stale_after_hours=(
            stale_after_hours
        )
    )


# ============================================================
# ACTIVE JOBS
# ============================================================


@router.get("/lifecycle/active")
def get_active_job_list(
    db: Session = Depends(get_db)
):

    jobs = get_active_jobs(
        db
    )

    return {
        "success": True,

        "total_active_jobs": len(
            jobs
        ),

        "jobs": [
            {
                "job_id": job.id,

                "pipeline_run_id": (
                    job.pipeline_run_id
                ),

                "title": job.title,

                "company": job.company,

                "location": job.location,

                "source": job.source,

                "url": job.url,

                "match_score": (
                    job.match_score
                ),

                "priority_score": (
                    job.priority_score
                ),

                "salary_min": (
                    job.salary_min
                ),

                "salary_max": (
                    job.salary_max
                ),

                "status": job.status,

                "discovered_at": (
                    job.discovered_at
                ),

                "last_seen_at": (
                    job.last_seen_at
                )
            }
            for job in jobs
        ]
    }


# ============================================================
# STALE JOBS
# ============================================================


@router.get("/lifecycle/stale")
def get_stale_job_list(
    db: Session = Depends(get_db)
):

    jobs = get_stale_jobs(
        db
    )

    return {
        "success": True,

        "total_stale_jobs": len(
            jobs
        ),

        "jobs": [
            {
                "job_id": job.id,

                "pipeline_run_id": (
                    job.pipeline_run_id
                ),

                "title": job.title,

                "company": job.company,

                "location": job.location,

                "source": job.source,

                "url": job.url,

                "match_score": (
                    job.match_score
                ),

                "priority_score": (
                    job.priority_score
                ),

                "salary_min": (
                    job.salary_min
                ),

                "salary_max": (
                    job.salary_max
                ),

                "status": job.status,

                "discovered_at": (
                    job.discovered_at
                ),

                "last_seen_at": (
                    job.last_seen_at
                )
            }
            for job in jobs
        ]
    }


# ============================================================
# PIPELINE RUN HISTORY
# ============================================================


@router.get("/pipeline-runs")
def get_pipeline_runs(
    limit: int = 20,
    db: Session = Depends(get_db)
):

    limit = max(
        1,
        min(limit, 100)
    )

    runs = (
        db.query(PipelineRun)
        .order_by(
            PipelineRun.id.desc()
        )
        .limit(limit)
        .all()
    )

    return {
        "success": True,

        "count": len(runs),

        "runs": [
            {
                "id": run.id,

                "started_at": (
                    run.started_at
                ),

                "completed_at": (
                    run.completed_at
                ),

                "status": run.status,

                "search_title": (
                    run.search_title
                ),

                "search_location": (
                    run.search_location
                ),

                "jobs_found": (
                    run.jobs_found
                ),

                "jobs_saved": (
                    run.jobs_saved
                ),

                "applications_prepared": (
                    run.applications_prepared
                ),

                "error_message": (
                    run.error_message
                )
            }
            for run in runs
        ]
    }


# ============================================================
# SINGLE PIPELINE RUN
# ============================================================


@router.get(
    "/pipeline-runs/{run_id}"
)
def get_pipeline_run(
    run_id: int,
    db: Session = Depends(get_db)
):

    run = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.id == run_id
        )
        .first()
    )

    if run is None:

        return {
            "success": False,

            "message": (
                "Pipeline run not found"
            )
        }

    return {
        "success": True,

        "run": {
            "id": run.id,

            "started_at": (
                run.started_at
            ),

            "completed_at": (
                run.completed_at
            ),

            "status": run.status,

            "search_title": (
                run.search_title
            ),

            "search_location": (
                run.search_location
            ),

            "jobs_found": (
                run.jobs_found
            ),

            "jobs_saved": (
                run.jobs_saved
            ),

            "applications_prepared": (
                run.applications_prepared
            ),

            "error_message": (
                run.error_message
            )
        }
    }


# ============================================================
# PIPELINE RUN APPLICATIONS
# ============================================================


@router.get(
    "/pipeline-runs/{run_id}/applications"
)
def get_pipeline_run_applications(
    run_id: int,
    db: Session = Depends(get_db)
):

    pipeline_run = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.id == run_id
        )
        .first()
    )

    if pipeline_run is None:

        return {
            "success": False,

            "message": (
                "Pipeline run not found"
            )
        }

    applications = (
        db.query(Application)
        .filter(
            Application.pipeline_run_id
            == run_id
        )
        .all()
    )

    return {
        "success": True,

        "pipeline_run_id": run_id,

        "pipeline_status": (
            pipeline_run.status
        ),

        "total_applications": len(
            applications
        ),

        "applications": [
            {
                "application_id": (
                    application.id
                ),

                "pipeline_run_id": (
                    application.pipeline_run_id
                ),

                "job_id": (
                    application.job_id
                ),

                "status": (
                    application.status
                ),

                "mode": (
                    application.mode
                ),

                "approval_required": (
                    application.approval_required
                ),

                "approved": (
                    application.approved
                ),

                "resume_file": (
                    application.resume_file
                ),

                "cover_letter_file": (
                    application.cover_letter_file
                ),

                "applied_at": (
                    application.applied_at
                ),

                "notes": (
                    application.notes
                )
            }
            for application in applications
        ]
    }


# ============================================================
# DASHBOARD
# ============================================================


@router.get("/dashboard")
def get_dashboard(
    db: Session = Depends(get_db)
):

    total_jobs = (
        db.query(Job)
        .count()
    )

    analyzed_jobs = (
        db.query(Job)
        .filter(
            Job.status == "ANALYZED"
        )
        .count()
    )

    active_jobs = (
        db.query(Job)
        .filter(
            Job.status == "ACTIVE"
        )
        .count()
    )

    stale_jobs = (
        db.query(Job)
        .filter(
            Job.status == "STALE"
        )
        .count()
    )

    total_applications = (
        db.query(Application)
        .count()
    )

    pending_approvals = (
        db.query(Application)
        .filter(
            Application.status == "PREPARED",

            Application.mode
            == "APPROVAL_REQUIRED",

            Application.approval_required
            == 1,

            Application.approved
            == 0
        )
        .count()
    )

    approved_applications = (
        db.query(Application)
        .filter(
            Application.status == "APPROVED",

            Application.approved == 1
        )
        .count()
    )

    applied_applications = (
        db.query(Application)
        .filter(
            Application.status == "APPLIED"
        )
        .count()
    )

    rejected_applications = (
        db.query(Application)
        .filter(
            Application.status == "REJECTED"
        )
        .count()
    )

    total_pipeline_runs = (
        db.query(PipelineRun)
        .count()
    )

    completed_pipeline_runs = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.status == "COMPLETED"
        )
        .count()
    )

    failed_pipeline_runs = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.status == "FAILED"
        )
        .count()
    )

    running_pipeline_runs = (
        db.query(PipelineRun)
        .filter(
            PipelineRun.status == "RUNNING"
        )
        .count()
    )

    scheduler_settings = (
        get_scheduler_settings()
    )

    jobs = scheduler.get_jobs()

    next_run_time = None

    if jobs:

        next_run_time = (
            jobs[0].next_run_time.isoformat()
            if jobs[0].next_run_time
            else None
        )

    latest_pipeline_run = (
        db.query(PipelineRun)
        .order_by(
            PipelineRun.id.desc()
        )
        .first()
    )

    latest_run = None

    if latest_pipeline_run:

        latest_run = {
            "id": (
                latest_pipeline_run.id
            ),

            "started_at": (
                latest_pipeline_run.started_at
            ),

            "completed_at": (
                latest_pipeline_run.completed_at
            ),

            "status": (
                latest_pipeline_run.status
            ),

            "search_title": (
                latest_pipeline_run.search_title
            ),

            "search_location": (
                latest_pipeline_run.search_location
            ),

            "jobs_found": (
                latest_pipeline_run.jobs_found
            ),

            "jobs_saved": (
                latest_pipeline_run.jobs_saved
            ),

            "applications_prepared": (
                latest_pipeline_run
                .applications_prepared
            ),

            "error_message": (
                latest_pipeline_run
                .error_message
            )
        }

    return {
        "success": True,

        "scheduler": {
            "running": (
                scheduler.running
            ),

            "search_title": (
                scheduler_settings[
                    "search_title"
                ]
            ),

            "search_location": (
                scheduler_settings[
                    "search_location"
                ]
            ),

            "interval_hours": (
                scheduler_settings[
                    "interval_hours"
                ]
            ),

            "max_pages": (
                scheduler_settings[
                    "max_pages"
                ]
            ),

            "results_per_page": (
                scheduler_settings[
                    "results_per_page"
                ]
            ),

            "next_run_time": (
                next_run_time
            )
        },

        "jobs": {
            "total": total_jobs,

            "analyzed": analyzed_jobs,

            "active": active_jobs,

            "stale": stale_jobs
        },

        "applications": {
            "total": (
                total_applications
            ),

            "pending_approval": (
                pending_approvals
            ),

            "approved": (
                approved_applications
            ),

            "applied": (
                applied_applications
            ),

            "rejected": (
                rejected_applications
            )
        },

        "pipeline_runs": {
            "total": (
                total_pipeline_runs
            ),

            "completed": (
                completed_pipeline_runs
            ),

            "running": (
                running_pipeline_runs
            ),

            "failed": (
                failed_pipeline_runs
            )
        },

        "latest_pipeline_run": (
            latest_run
        ),

        "approval_required": True
    }