from typing import Optional

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

from app.services.logger import logger


def run_job_search_pipeline(
    db: Session,
    search_title: Optional[str] = None,
    search_location: Optional[str] = None,
    max_pages: Optional[int] = None,
    results_per_page: Optional[int] = None
):
    """
    Run the complete automated job-search pipeline.

    Pipeline:

    1. Create PipelineRun
    2. Fetch jobs
    3. Check preferences
    4. Analyze JD
    5. Calculate skill match
    6. Apply salary filtering
    7. Calculate priority
    8. Save accepted jobs
    9. Track jobs against PipelineRun
    10. Select ACTIVE jobs only
    11. Prepare application documents
    12. Keep applications waiting for approval
    13. Complete PipelineRun
    """

    # __define-ocg__

    logger.info(
        "Starting job-search pipeline"
    )

    started_at = (
        datetime.now().isoformat()
    )

    pipeline_run = PipelineRun(
        started_at=started_at,
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

    pipeline_run_id = (
        pipeline_run.id
    )

    logger.info(
        f"Pipeline run created: "
        f"{pipeline_run_id}"
    )

    try:

        result = discover_jobs_from_source(
            db=db,
            search_title=search_title,
            search_location=search_location,
            max_pages=max_pages,
            results_per_page=results_per_page,
            pipeline_run_id=pipeline_run_id
        )

        logger.info(
            f"Job discovery completed for "
            f"pipeline run {pipeline_run_id}: "
            f"{result.get('total_jobs_found', 0)} "
            f"jobs found, "
            f"{result.get('jobs_saved', 0)} "
            f"jobs saved"
        )

        prepared_applications = []

        preparation_limit = 5

        current_run_job_ids = result.get(
            "current_run_job_ids",
            []
        )

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
                    Job.status == "ACTIVE"
                )
                .order_by(
                    Job.priority_score.desc()
                )
                .limit(
                    preparation_limit
                )
                .all()
            )

        for varPcb, job in enumerate(
            qualifying_jobs,
            start=1
        ):
            # __define-pcb__

            if job.status != "ACTIVE":
                continue

            preparation_result = (
                generate_application_documents(
                    db=db,
                    job_id=job.id
                )
            )

            prepared_applications.append(
                {
                    "rank": varPcb,
                    "job_id": job.id,
                    "pipeline_run_id": (
                        pipeline_run_id
                    ),
                    "title": job.title,
                    "company": job.company,
                    "job_status": job.status,
                    "priority_score": (
                        job.priority_score
                    ),
                    "preparation": (
                        preparation_result
                    )
                }
            )

        logger.info(
            f"Applications prepared for "
            f"pipeline run {pipeline_run_id}: "
            f"{len(prepared_applications)}"
        )

        search_summary = {
            "total_jobs_found": (
                result.get(
                    "total_jobs_found",
                    0
                )
            ),
            "jobs_saved": (
                result.get(
                    "jobs_saved",
                    0
                )
            ),
            "duplicates": (
                result.get(
                    "duplicates",
                    0
                )
            ),
            "rejected_by_preferences": (
                result.get(
                    "rejected_by_preferences",
                    0
                )
            ),
            "rejected_by_match_score": (
                result.get(
                    "rejected_by_match_score",
                    0
                )
            ),
            "rejected_by_salary": (
                result.get(
                    "rejected_by_salary",
                    0
                )
            ),
            "missing_url": (
                result.get(
                    "missing_url",
                    0
                )
            )
        }

        pipeline_run.jobs_found = (
            search_summary[
                "total_jobs_found"
            ]
        )

        pipeline_run.jobs_saved = (
            search_summary[
                "jobs_saved"
            ]
        )

        pipeline_run.applications_prepared = (
            len(prepared_applications)
        )

        pipeline_run.completed_at = (
            datetime.now().isoformat()
        )

        pipeline_run.status = "COMPLETED"

        db.commit()

        db.refresh(pipeline_run)

        logger.info(
            f"Pipeline run "
            f"{pipeline_run_id} "
            f"completed successfully"
        )

        return {
            "success": True,
            "pipeline_run_id": (
                pipeline_run.id
            ),
            "pipeline_run_status": (
                pipeline_run.status
            ),
            "message": (
                "Automated job-search and "
                "application-preparation "
                "pipeline completed"
            ),
            "pipeline": [
                "PIPELINE_RUN_CREATED",
                "JOB_DISCOVERY",
                "PREFERENCE_FILTER",
                "JD_ANALYSIS",
                "SKILL_MATCHING",
                "SALARY_FILTER",
                "PRIORITY_RANKING",
                "DATABASE_STORAGE",
                "CURRENT_RUN_SELECTION",
                "ACTIVE_JOB_FILTER",
                "APPLICATION_PREPARATION",
                "APPROVAL_REQUIRED",
                "PIPELINE_RUN_COMPLETED"
            ],
            "search_summary": search_summary,
            "current_run_job_ids": (
                current_run_job_ids
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
            "note": (
                "Only ACTIVE jobs are selected "
                "for new application preparation. "
                "Applications are prepared but "
                "not submitted automatically."
            )
        }

    except Exception as error:

        pipeline_run.status = "FAILED"

        pipeline_run.completed_at = (
            datetime.now().isoformat()
        )

        pipeline_run.error_message = str(
            error
        )

        db.commit()

        logger.exception(
            f"Pipeline run "
            f"{pipeline_run_id} "
            f"failed: {error}"
        )

        return {
            "success": False,
            "pipeline_run_id": (
                pipeline_run.id
            ),
            "pipeline_run_status": (
                pipeline_run.status
            ),
            "message": (
                "Automated job-search "
                "pipeline failed"
            ),
            "error": str(error)
        }