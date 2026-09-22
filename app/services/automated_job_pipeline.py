from datetime import datetime

from sqlalchemy.orm import Session

from app.models.job import Job
from app.models.pipeline_run import PipelineRun

from app.services.job_search_service import (
    discover_jobs_from_source
)

from app.services.job_resume_service import (
    generate_application_documents
)


# ---------------------------------------------------------
# Application preparation settings
# ---------------------------------------------------------

ALLOWED_JOB_TYPES = [
    "Full-time",
    "Contract"
]

ALLOWED_JOB_STATUSES = [
    "ACTIVE",
    "ANALYZED"
]

PREPARATION_LIMIT = 5


def run_job_search_pipeline(
    db: Session,
    search_title: str,
    search_location: str,
    max_pages: int,
    results_per_page: int
):
    """
    Run the complete automated job-search pipeline.

    Pipeline:

    1. Create a PipelineRun.
    2. Discover jobs from the configured source.
    3. Save/analyze discovered jobs.
    4. Identify jobs belonging to this pipeline run.
    5. Filter eligible jobs.
    6. Select the highest-priority eligible jobs.
    7. Generate application documents.
    8. Put successful applications into PENDING_APPROVAL.
    9. Never submit applications automatically.
    """

    # -----------------------------------------------------
    # STEP 1: Create pipeline run
    # -----------------------------------------------------

    pipeline_run = PipelineRun(
        started_at=datetime.now().isoformat(),
        status="RUNNING",
        search_title=search_title,
        search_location=search_location,
        jobs_found=0,
        jobs_saved=0,
        applications_prepared=0
    )

    db.add(pipeline_run)
    db.commit()
    db.refresh(pipeline_run)

    pipeline_run_id = pipeline_run.id

    try:

        # -------------------------------------------------
        # STEP 2: Discover jobs
        # -------------------------------------------------

        search_result = discover_jobs_from_source(
            db=db,
            search_title=search_title,
            search_location=search_location,
            max_pages=max_pages,
            results_per_page=results_per_page,
            pipeline_run_id=pipeline_run_id
        )

        # -------------------------------------------------
        # STEP 3: Extract search statistics
        # -------------------------------------------------

        if isinstance(search_result, dict):

            jobs_found = search_result.get(
                "total_jobs_found",
                search_result.get(
                    "jobs_found",
                    0
                )
            )

            jobs_saved = search_result.get(
                "jobs_saved",
                0
            )

        else:

            jobs_found = 0
            jobs_saved = 0

        pipeline_run.jobs_found = jobs_found
        pipeline_run.jobs_saved = jobs_saved

        db.commit()

        # -------------------------------------------------
        # STEP 4: Get jobs belonging to this pipeline run
        # -------------------------------------------------

        current_run_jobs = (
            db.query(Job)
            .filter(
                Job.pipeline_run_id
                == pipeline_run_id
            )
            .all()
        )

        current_run_job_ids = [
            job.id
            for job in current_run_jobs
        ]

        # -------------------------------------------------
        # STEP 5: Filter eligible jobs
        #
        # A job must:
        #
        # - Belong to this pipeline run
        # - Be ACTIVE or ANALYZED
        # - Have a known job type
        # - Be Full-time or Contract
        #
        # We do NOT guess missing job types.
        # -------------------------------------------------

        qualifying_jobs = []

        if current_run_job_ids:

            qualifying_jobs = (
                db.query(Job)
                .filter(
                    Job.id.in_(
                        current_run_job_ids
                    ),

                    Job.pipeline_run_id
                    == pipeline_run_id,

                    Job.status.in_(
                        ALLOWED_JOB_STATUSES
                    ),

                    Job.job_type.isnot(
                        None
                    ),

                    Job.job_type.in_(
                        ALLOWED_JOB_TYPES
                    )
                )
                .order_by(
                    Job.priority_score.desc()
                )
                .limit(
                    PREPARATION_LIMIT
                )
                .all()
            )

        # -------------------------------------------------
        # STEP 6: Prepare applications
        # -------------------------------------------------

        prepared_applications = []

        for rank, job in enumerate(
            qualifying_jobs,
            start=1
        ):

            preparation_result = (
                generate_application_documents(
                    db=db,
                    job_id=job.id
                )
            )

            # ---------------------------------------------
            # Only count successful preparations
            # ---------------------------------------------

            if preparation_result.get(
                "success"
            ):

                prepared_applications.append(
                    {
                        "rank": rank,

                        "job_id": job.id,

                        "pipeline_run_id": (
                            pipeline_run_id
                        ),

                        "title": job.title,

                        "company": job.company,

                        "job_type": job.job_type,

                        "job_status": job.status,

                        "match_score": (
                            job.match_score
                        ),

                        "priority_score": (
                            job.priority_score
                        ),

                        "preparation": (
                            preparation_result
                        )
                    }
                )

        # -------------------------------------------------
        # STEP 7: Update pipeline status
        # -------------------------------------------------

        pipeline_run.applications_prepared = (
            len(prepared_applications)
        )

        pipeline_run.status = "COMPLETED"

        pipeline_run.completed_at = (
            datetime.now().isoformat()
        )

        db.commit()
        db.refresh(pipeline_run)

        # -------------------------------------------------
        # STEP 8: Return successful pipeline result
        # -------------------------------------------------

        return {
            "success": True,

            "pipeline_run_id": (
                pipeline_run_id
            ),

            "pipeline_run_status": (
                pipeline_run.status
            ),

            "message": (
                "Automated job-search and "
                "application-preparation "
                "pipeline completed"
            ),

            "search_summary": (
                search_result
            ),

            "current_run_job_ids": (
                current_run_job_ids
            ),

            "eligible_jobs_found": (
                len(qualifying_jobs)
            ),

            "active_jobs_selected": (
                len(qualifying_jobs)
            ),

            "applications_prepared": (
                len(prepared_applications)
            ),

            "prepared_applications": (
                prepared_applications
            ),

            "approval_required": True,

            "allowed_job_types": (
                ALLOWED_JOB_TYPES
            ),

            "allowed_job_statuses": (
                ALLOWED_JOB_STATUSES
            ),

            "preparation_limit": (
                PREPARATION_LIMIT
            ),

            "note": (
                "Only ACTIVE or ANALYZED jobs "
                "with a confirmed Full-time or "
                "Contract job type are selected "
                "for application preparation. "
                "Applications require user approval "
                "and are not submitted automatically."
            )
        }

    except Exception as error:

        # -------------------------------------------------
        # STEP 9: Handle pipeline failure
        # -------------------------------------------------

        pipeline_run.status = "FAILED"

        pipeline_run.completed_at = (
            datetime.now().isoformat()
        )

        pipeline_run.error_message = str(
            error
        )

        db.commit()

        return {
            "success": False,

            "pipeline_run_id": (
                pipeline_run_id
            ),

            "pipeline_run_status": (
                pipeline_run.status
            ),

            "message": (
                "Automated job-search and "
                "application-preparation "
                "pipeline failed"
            ),

            "error": str(error)
        }