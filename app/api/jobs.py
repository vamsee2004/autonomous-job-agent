from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.job import Job
from app.models.application import Application

from app.services.job_source import fetch_jobs
from app.services.job_search_service import discover_jobs_from_source
from app.services.application_limits import (
    check_application_limits
)
from app.services.portal_permissions import (
    check_portal_permission
)
from app.services.portal_adapter_factory import (
    get_portal_adapter
)
from app.services.application_state_machine import (
    can_transition,
    normalize_status
)
from app.services.logger import logger


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# ============================================================
# DATABASE DEPENDENCY
# ============================================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================================
# REQUEST MODELS
# ============================================================

class JobSearchRequest(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None

    max_pages: int = Field(
        default=1,
        ge=1,
        le=10
    )

    results_per_page: int = Field(
        default=10,
        ge=1,
        le=50
    )


class ApplicationStatusRequest(BaseModel):
    status: str = Field(
        min_length=1,
        max_length=50
    )


class ApplicationFeedbackRequest(BaseModel):
    outcome: str = Field(
        min_length=1,
        max_length=50
    )

    feedback: Optional[str] = Field(
        default=None,
        max_length=2000
    )


# ============================================================
# BASIC JOB ENDPOINTS
# ============================================================

@router.get("/")
def get_jobs(
    db: Session = Depends(get_db)
):
    try:
        jobs = (
            db.query(Job)
            .order_by(
                Job.priority_score.desc(),
                Job.id.desc()
            )
            .all()
        )

        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }

    except Exception:
        logger.exception("Failed to retrieve jobs.")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve jobs."
        )


@router.get("/search")
def search_jobs(
    title: Optional[str] = Query(
        default=None
    ),
    location: Optional[str] = Query(
        default=None
    ),
    max_pages: int = Query(
        default=1,
        ge=1,
        le=10
    ),
    results_per_page: int = Query(
        default=10,
        ge=1,
        le=50
    )
):
    try:
        jobs = fetch_jobs(
            search_title=title,
            search_location=location,
            max_pages=max_pages,
            results_per_page=results_per_page
        )

        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs
        }

    except Exception:
        logger.exception("Job search failed.")

        raise HTTPException(
            status_code=500,
            detail="Job search failed."
        )


@router.post("/discover")
def discover_jobs(
    request: JobSearchRequest,
    db: Session = Depends(get_db)
):
    try:
        result = discover_jobs_from_source(
            db=db,
            search_title=request.title,
            search_location=request.location,
            max_pages=request.max_pages,
            results_per_page=request.results_per_page
        )

        return result

    except Exception:
        db.rollback()

        logger.exception(
            "Job discovery failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Job discovery failed."
        )


# ============================================================
# GET SINGLE JOB
# ============================================================

@router.get("/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    try:
        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found."
            )

        return {
            "success": True,
            "job": job
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            f"Failed to retrieve job {job_id}."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve job."
        )


# ============================================================
# CREATE APPLICATION
# ============================================================

@router.post("/{job_id}/apply")
def create_application(
    job_id: int,
    db: Session = Depends(get_db)
):
    try:
        job = (
            db.query(Job)
            .filter(Job.id == job_id)
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Job not found."
            )

        # ----------------------------------------------------
        # Allowed job types
        # ----------------------------------------------------

        allowed_job_types = {
            "Full-time",
            "Contract"
        }

        if job.job_type not in allowed_job_types:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "JOB_TYPE_NOT_ALLOWED",
                    "job_type": job.job_type,
                    "allowed_job_types": sorted(
                        allowed_job_types
                    )
                }
            )

        # ----------------------------------------------------
        # Duplicate application check
        # ----------------------------------------------------

        existing_application = (
            db.query(Application)
            .filter(
                Application.job_id == job_id
            )
            .first()
        )

        if existing_application:
            return {
                "success": False,
                "message": (
                    "Application already exists "
                    "for this job."
                ),
                "application_id": (
                    existing_application.id
                ),
                "status": (
                    existing_application.status
                )
            }

        # ----------------------------------------------------
        # Application limits
        # ----------------------------------------------------

        limit_result = check_application_limits(
            db=db,
            job=job
        )

        if not limit_result.get("allowed", False):
            raise HTTPException(
                status_code=429,
                detail=limit_result
            )

        # ----------------------------------------------------
        # Portal permission
        # ----------------------------------------------------

        portal_name = job.source or "Adzuna"

        permission_result = check_portal_permission(
            portal_name
        )

        if not permission_result.get(
            "allowed",
            False
        ):
            raise HTTPException(
                status_code=403,
                detail=permission_result
            )

        # ----------------------------------------------------
        # Create application
        # ----------------------------------------------------

        application = Application(
            job_id=job.id,
            status="PENDING_APPROVAL",
            mode="APPROVAL_REQUIRED",
            approved=0
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        logger.info(
            f"Application {application.id} "
            f"created for job {job.id}."
        )

        return {
            "success": True,
            "message": (
                "Application created and "
                "is waiting for approval."
            ),
            "application": application
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        logger.exception(
            f"Failed to create application "
            f"for job {job_id}."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create application."
        )


# ============================================================
# LIST APPLICATIONS
# ============================================================

@router.get("/applications/")
def get_applications(
    status: Optional[str] = Query(
        default=None
    ),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Application)

        if status:
            normalized_status = normalize_status(
                status
            )

            query = query.filter(
                Application.status
                == normalized_status
            )

        applications = (
            query
            .order_by(
                Application.id.desc()
            )
            .all()
        )

        return {
            "success": True,
            "count": len(applications),
            "applications": applications
        }

    except Exception:
        logger.exception(
            "Failed to retrieve applications."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve applications."
        )


# ============================================================
# GET SINGLE APPLICATION
# ============================================================

@router.get("/applications/{application_id}")
def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=404,
                detail="Application not found."
            )

        return {
            "success": True,
            "application": application
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            f"Failed to retrieve "
            f"application {application_id}."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve application."
        )


# ============================================================
# UPDATE APPLICATION STATUS
# STATE MACHINE ENFORCED
# ============================================================

@router.put(
    "/applications/{application_id}/status"
)
def update_application_status(
    application_id: int,
    request: ApplicationStatusRequest,
    db: Session = Depends(get_db)
):
    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=404,
                detail="Application not found."
            )

        transition = can_transition(
            application.status,
            request.status
        )

        if not transition["allowed"]:
            raise HTTPException(
                status_code=400,
                detail=transition
            )

        new_status = normalize_status(
            request.status
        )

        application.status = new_status

        db.commit()
        db.refresh(application)

        logger.info(
            f"Application {application_id} "
            f"status changed to {new_status}."
        )

        return {
            "success": True,
            "message": (
                "Application status updated."
            ),
            "transition": transition,
            "application": application
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        logger.exception(
            f"Failed to update status "
            f"for application {application_id}."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update application status."
        )


# ============================================================
# MARK APPLICATION READY
# ============================================================

@router.post(
    "/applications/{application_id}/ready"
)
def mark_application_ready(
    application_id: int,
    db: Session = Depends(get_db)
):
    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=404,
                detail="Application not found."
            )

        transition = can_transition(
            application.status,
            "READY"
        )

        if not transition["allowed"]:
            raise HTTPException(
                status_code=400,
                detail=transition
            )

        application.status = "READY"

        db.commit()
        db.refresh(application)

        logger.info(
            f"Application {application_id} "
            f"marked READY."
        )

        return {
            "success": True,
            "message": (
                "Application marked as READY."
            ),
            "transition": transition,
            "application": application
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        logger.exception(
            f"Failed to mark application "
            f"{application_id} as READY."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to mark application as READY."
        )


# ============================================================
# APPROVE APPLICATION
# ============================================================

@router.post(
    "/applications/{application_id}/approve"
)
def approve_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=404,
                detail="Application not found."
            )

        if application.approved == 1:
            return {
                "success": True,
                "message": (
                    "Application is already approved."
                ),
                "application": application
            }

        transition = can_transition(
            application.status,
            "APPROVED"
        )

        if not transition["allowed"]:
            raise HTTPException(
                status_code=400,
                detail=transition
            )

        application.status = "APPROVED"
        application.approved = 1

        db.commit()
        db.refresh(application)

        logger.info(
            f"Application {application_id} "
            f"approved."
        )

        return {
            "success": True,
            "message": (
                "Application approved."
            ),
            "transition": transition,
            "application": application
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        logger.exception(
            f"Failed to approve "
            f"application {application_id}."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to approve application."
        )


# ============================================================
# SUBMIT APPLICATION
# STATE MACHINE + PORTAL ADAPTER
# ============================================================

@router.post(
    "/applications/{application_id}/submit"
)
def submit_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=404,
                detail="Application not found."
            )

        # ----------------------------------------------------
        # Already submitted
        # ----------------------------------------------------

        if application.status == "SUBMITTED":
            return {
                "success": False,
                "message": (
                    "Application is already submitted."
                ),
                "application": application
            }

        # ----------------------------------------------------
        # State machine validation
        # ----------------------------------------------------

        transition = can_transition(
            application.status,
            "SUBMITTED"
        )

        if not transition["allowed"]:
            raise HTTPException(
                status_code=400,
                detail=transition
            )

        # ----------------------------------------------------
        # Approval validation
        # ----------------------------------------------------

        if application.status != "APPROVED":
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "APPLICATION_NOT_APPROVED",
                    "status": application.status
                }
            )

        if application.approved != 1:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": (
                        "APPLICATION_APPROVAL_FLAG_NOT_SET"
                    )
                }
            )

        # ----------------------------------------------------
        # Get associated job
        # ----------------------------------------------------

        job = (
            db.query(Job)
            .filter(
                Job.id == application.job_id
            )
            .first()
        )

        if not job:
            raise HTTPException(
                status_code=404,
                detail="Associated job not found."
            )

        # ----------------------------------------------------
        # Portal
        # ----------------------------------------------------

        portal_name = job.source or "Adzuna"

        permission_result = check_portal_permission(
            portal_name
        )

        if not permission_result.get(
            "allowed",
            False
        ):
            raise HTTPException(
                status_code=403,
                detail=permission_result
            )

        # ----------------------------------------------------
        # Portal adapter
        # ----------------------------------------------------

        adapter = get_portal_adapter(
            portal_name
        )

        if adapter is None:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "PORTAL_ADAPTER_NOT_FOUND",
                    "portal": portal_name
                }
            )

        # ----------------------------------------------------
        # External submission
        # ----------------------------------------------------

        try:
            submission_result = (
                adapter.submit_application(
                    application
                )
            )

        except Exception:
            logger.exception(
                f"Portal adapter failed for "
                f"application {application_id}."
            )

            raise HTTPException(
                status_code=502,
                detail=(
                    "Portal adapter failed while "
                    "processing the application."
                )
            )

        # ----------------------------------------------------
        # Only mark submitted if adapter succeeds
        # ----------------------------------------------------

        if not submission_result.get(
            "success",
            False
        ):
            return {
                "success": False,
                "message": (
                    "Application was not submitted "
                    "because the portal adapter "
                    "did not complete submission."
                ),
                "submission": submission_result,
                "application": application
            }

        application.status = "SUBMITTED"

        db.commit()
        db.refresh(application)

        logger.info(
            f"Application {application_id} "
            f"successfully submitted."
        )

        return {
            "success": True,
            "message": (
                "Application submitted successfully."
            ),
            "transition": transition,
            "submission": submission_result,
            "application": application
        }

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        logger.exception(
            f"Failed to submit "
            f"application {application_id}."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to submit application."
        )


# ============================================================
# APPLICATION FEEDBACK
# ============================================================

@router.post(
    "/applications/{application_id}/feedback"
)
def add_application_feedback(
    application_id: int,
    request: ApplicationFeedbackRequest,
    db: Session = Depends(get_db)
):
    try:
        application = (
            db.query(Application)
            .filter(
                Application.id == application_id
            )
            .first()
        )

        if not application:
            raise HTTPException(
                status_code=404,
                detail="Application not found."
            )

        from app.services.application_feedback_service import (
            record_application_feedback
        )

        result = record_application_feedback(
            db=db,
            application_id=application_id,
            outcome=request.outcome,
            feedback=request.feedback
        )

        return result

    except HTTPException:
        raise

    except Exception:
        db.rollback()

        logger.exception(
            f"Failed to record feedback "
            f"for application {application_id}."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to record application feedback."
        )


# ============================================================
# APPLICATION ANALYTICS
# ============================================================

@router.get(
    "/applications/analytics/summary"
)
def application_analytics_summary(
    db: Session = Depends(get_db)
):
    try:
        from app.services.application_analytics_service import (
            get_application_analytics
        )

        return get_application_analytics(
            db=db
        )

    except Exception:
        logger.exception(
            "Failed to generate application analytics."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate application analytics."
        )


# ============================================================
# DETAILED APPLICATION ANALYTICS
# ============================================================

@router.get(
    "/applications/analytics/detailed"
)
def application_detailed_analytics(
    db: Session = Depends(get_db)
):
    try:
        from app.services.detailed_analytics_service import (
            get_detailed_application_analytics
        )

        return get_detailed_application_analytics(
            db=db
        )

    except Exception:
        logger.exception(
            "Failed to generate detailed analytics."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to generate detailed analytics."
            )
        )


# ============================================================
# LEARNING SUMMARY
# ============================================================

@router.get(
    "/applications/learning/summary"
)
def application_learning_summary(
    db: Session = Depends(get_db)
):
    try:
        from app.services.application_learning_service import (
            get_learning_summary
        )

        return get_learning_summary(
            db=db
        )

    except Exception:
        logger.exception(
            "Failed to generate learning summary."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate learning summary."
        )


# ============================================================
# ALL APPLICATION FEEDBACK
# ============================================================

@router.get(
    "/applications/feedback/all"
)
def get_all_application_feedback(
    db: Session = Depends(get_db)
):
    try:
        from app.services.application_feedback_service import (
            get_all_feedback
        )

        return get_all_feedback(
            db=db
        )

    except Exception:
        logger.exception(
            "Failed to retrieve application feedback."
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve application feedback."
        )