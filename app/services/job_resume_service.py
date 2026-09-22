from pathlib import Path

from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.application import Application

from app.resume.resume_generator import (
    generate_job_resume
)

from app.services.cover_letter_generator import (
    generate_cover_letter
)

from app.services.application_limits import (
    check_application_limits
)

from app.services.logger import logger


def file_exists(file_path):

    if not file_path:
        return False

    return Path(file_path).exists()


def generate_application_documents(
    db: Session,
    job_id: int
):

    logger.info(
        f"Starting application preparation: "
        f"job_id={job_id}"
    )

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if job is None:

        logger.warning(
            f"Application preparation failed: "
            f"job_id={job_id} not found"
        )

        return {
            "success": False,
            "message": "Job not found"
        }

    logger.info(
        f"Preparing application for job: "
        f"job_id={job.id}, "
        f"title='{job.title}', "
        f"company='{job.company}', "
        f"status={job.status}"
    )

    # --------------------------------------------------
    # STALE JOB CHECK
    # --------------------------------------------------

    if job.status == "STALE":

        logger.warning(
            f"Application preparation blocked: "
            f"job_id={job.id} is STALE"
        )

        return {
            "success": False,
            "message": (
                "Application preparation is blocked "
                "because this job is stale"
            ),
            "job_id": job.id,
            "pipeline_run_id": job.pipeline_run_id,
            "status": job.status,
            "last_seen_at": job.last_seen_at
        }

    # --------------------------------------------------
    # JOB STATUS CHECK
    # --------------------------------------------------

    if job.status not in [
        "ACTIVE",
        "ANALYZED"
    ]:

        logger.warning(
            f"Application preparation blocked: "
            f"job_id={job.id}, "
            f"status={job.status}"
        )

        return {
            "success": False,
            "message": (
                "Job is not available for "
                "application preparation"
            ),
            "job_id": job.id,
            "status": job.status
        }

    # --------------------------------------------------
    # APPLICATION LIMIT CHECK
    # --------------------------------------------------

    limit_check = check_application_limits(
        db=db,
        job=job
    )

    if not limit_check["allowed"]:

        logger.warning(
            f"Application blocked by limits: "
            f"job_id={job.id}, "
            f"title='{job.title}', "
            f"company='{job.company}', "
            f"reason={limit_check['reason']}"
        )

        return {
            "success": False,
            "message": (
                "Application preparation blocked "
                "by application limits"
            ),
            "job_id": job.id,
            "pipeline_run_id": job.pipeline_run_id,
            "status": job.status,
            "limit_check": limit_check
        }

    logger.info(
        f"Application limits passed: "
        f"job_id={job.id}"
    )

    # --------------------------------------------------
    # DUPLICATE APPLICATION CHECK
    # --------------------------------------------------

    existing_application = (
        db.query(Application)
        .filter(
            Application.job_id == job.id
        )
        .first()
    )

    if existing_application:

        logger.info(
            f"Application already exists: "
            f"application_id="
            f"{existing_application.id}, "
            f"job_id={job.id}"
        )

        return {
            "success": False,
            "message": (
                "Application already exists "
                "for this job"
            ),
            "application_id": (
                existing_application.id
            ),
            "job_id": job.id,
            "pipeline_run_id": (
                existing_application.pipeline_run_id
            ),
            "status": (
                existing_application.status
            )
        }

    # --------------------------------------------------
    # RESUME GENERATION
    # --------------------------------------------------

    logger.info(
        f"Generating job-specific resume: "
        f"job_id={job.id}"
    )

    try:

        resume_file = generate_job_resume(
            job_title=job.title,
            company=job.company,
            job_description=job.description
        )

    except Exception as error:

        logger.exception(
            f"Resume generation failed: "
            f"job_id={job.id}: {error}"
        )

        return {
            "success": False,
            "message": "Resume generation failed",
            "job_id": job.id,
            "error": str(error)
        }

    resume_exists = file_exists(
        resume_file
    )

    if not resume_exists:

        logger.error(
            f"Resume file was not created: "
            f"job_id={job.id}, "
            f"file={resume_file}"
        )

        return {
            "success": False,
            "message": "Resume generation failed",
            "job_id": job.id
        }

    logger.info(
        f"Resume generated successfully: "
        f"job_id={job.id}, "
        f"file={resume_file}"
    )

    # --------------------------------------------------
    # COVER LETTER GENERATION
    # --------------------------------------------------

    logger.info(
        f"Generating cover letter: "
        f"job_id={job.id}"
    )

    try:

        cover_letter_file = (
            generate_cover_letter(
                job_title=job.title,
                company=job.company,
                job_description=job.description
            )
        )

    except Exception as error:

        logger.exception(
            f"Cover letter generation failed: "
            f"job_id={job.id}: {error}"
        )

        return {
            "success": False,
            "message": (
                "Cover letter generation failed"
            ),
            "job_id": job.id,
            "error": str(error)
        }

    cover_letter_exists = file_exists(
        cover_letter_file
    )

    if not cover_letter_exists:

        logger.error(
            f"Cover letter file was not created: "
            f"job_id={job.id}, "
            f"file={cover_letter_file}"
        )

        return {
            "success": False,
            "message": (
                "Cover letter generation failed"
            ),
            "job_id": job.id
        }

    logger.info(
        f"Cover letter generated successfully: "
        f"job_id={job.id}, "
        f"file={cover_letter_file}"
    )

    # --------------------------------------------------
    # CREATE APPLICATION RECORD
    # --------------------------------------------------

    application = Application(
        pipeline_run_id=job.pipeline_run_id,
        job_id=job.id,

        # Application is prepared and waiting
        # for explicit user approval.
        status="PENDING_APPROVAL",

        mode="APPROVAL_REQUIRED",

        resume_file=str(
            resume_file
        ),

        cover_letter_file=str(
            cover_letter_file
        ),

        notes=(
            "Resume and cover letter "
            "prepared successfully. "
            "Waiting for user approval."
        ),

        approval_required=1,
        approved=0
    )

    db.add(application)

    db.commit()

    db.refresh(application)

    logger.info(
        f"Application prepared successfully: "
        f"application_id={application.id}, "
        f"job_id={job.id}, "
        f"pipeline_run_id="
        f"{application.pipeline_run_id}, "
        f"status={application.status}, "
        f"approval_required="
        f"{application.approval_required}"
    )

    return {
        "success": True,

        "message": (
            "Application prepared and "
            "waiting for approval"
        ),

        "application_id": application.id,

        "pipeline_run_id": (
            application.pipeline_run_id
        ),

        "job_id": job.id,

        "job_title": job.title,

        "company": job.company,

        "job_status": job.status,

        "last_seen_at": job.last_seen_at,

        "status": application.status,

        "mode": application.mode,

        "approval_required": (
            application.approval_required
        ),

        "approved": application.approved,

        "resume_file": (
            application.resume_file
        ),

        "resume_exists": resume_exists,

        "cover_letter_file": (
            application.cover_letter_file
        ),

        "cover_letter_exists": (
            cover_letter_exists
        ),

        "limit_check": limit_check
    }


def generate_resume_for_job(
    db: Session,
    job_id: int
):

    logger.info(
        f"Starting resume generation: "
        f"job_id={job_id}"
    )

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if job is None:

        logger.warning(
            f"Resume generation failed: "
            f"job_id={job_id} not found"
        )

        return {
            "success": False,
            "message": "Job not found"
        }

    # --------------------------------------------------
    # STALE JOB CHECK
    # --------------------------------------------------

    if job.status == "STALE":

        logger.warning(
            f"Resume generation blocked: "
            f"job_id={job.id} is STALE"
        )

        return {
            "success": False,
            "message": (
                "Resume generation is blocked "
                "because this job is stale"
            ),
            "job_id": job.id,
            "status": job.status,
            "last_seen_at": job.last_seen_at
        }

    # --------------------------------------------------
    # JOB STATUS CHECK
    # --------------------------------------------------

    if job.status not in [
        "ACTIVE",
        "ANALYZED"
    ]:

        logger.warning(
            f"Resume generation blocked: "
            f"job_id={job.id}, "
            f"status={job.status}"
        )

        return {
            "success": False,
            "message": (
                "Job is not available "
                "for resume generation"
            ),
            "job_id": job.id,
            "status": job.status
        }

    # --------------------------------------------------
    # RESUME GENERATION
    # --------------------------------------------------

    try:

        resume_file = generate_job_resume(
            job_title=job.title,
            company=job.company,
            job_description=job.description
        )

    except Exception as error:

        logger.exception(
            f"Resume generation failed: "
            f"job_id={job.id}: {error}"
        )

        return {
            "success": False,
            "message": "Resume generation failed",
            "job_id": job.id,
            "error": str(error)
        }

    resume_exists = file_exists(
        resume_file
    )

    if resume_exists:

        logger.info(
            f"Resume generated successfully: "
            f"job_id={job.id}, "
            f"file={resume_file}"
        )

    else:

        logger.error(
            f"Resume file missing after generation: "
            f"job_id={job.id}, "
            f"file={resume_file}"
        )

    return {
        "success": resume_exists,
        "job_id": job.id,
        "pipeline_run_id": job.pipeline_run_id,
        "job_title": job.title,
        "company": job.company,
        "status": job.status,
        "last_seen_at": job.last_seen_at,
        "resume_file": str(resume_file),
        "resume_exists": resume_exists
    }