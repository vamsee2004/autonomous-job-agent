from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.database.connection import SessionLocal

from app.services.job_search_service import (
    discover_jobs_from_source
)

from app.services.job_lifecycle import (
    mark_stale_jobs
)

from app.services.outreach_follow_up_processor import (
    process_due_follow_ups
)

from app.services.config_validator import (
    get_configuration
)

from app.services.logger import (
    logger
)


# ============================================================
# SCHEDULER
# ============================================================

scheduler = BackgroundScheduler()


# ============================================================
# GET SCHEDULER SETTINGS
# ============================================================

def get_scheduler_settings():

    configuration = get_configuration()

    return {
        "search_title": (
            configuration[
                "job_search_title"
            ]
        ),

        "search_location": (
            configuration[
                "job_search_location"
            ]
        ),

        "search_interval_hours": (
            configuration[
                "job_search_interval_hours"
            ]
        ),

        "max_pages": (
            configuration[
                "job_search_max_pages"
            ]
        ),

        "results_per_page": (
            configuration[
                "job_search_results_per_page"
            ]
        ),

        "stale_after_hours": (
            configuration[
                "job_stale_after_hours"
            ]
        ),

        "automatic_stale_cleanup": (
            configuration[
                "automatic_stale_cleanup"
            ]
        ),

        "automatic_follow_up_processing": (
            configuration[
                "automatic_follow_up_processing"
            ]
        )
    }


# ============================================================
# RUN SCHEDULED JOB SEARCH
# ============================================================

def run_scheduled_job_search():

    settings = get_scheduler_settings()

    logger.info(
        "Running scheduled job search..."
    )

    logger.info(
        f"Search title: "
        f"{settings['search_title']}"
    )

    logger.info(
        f"Search location: "
        f"{settings['search_location']}"
    )

    db = SessionLocal()

    try:

        result = discover_jobs_from_source(
            db=db,
            search_title=(
                settings["search_title"]
            ),
            search_location=(
                settings["search_location"]
            ),
            max_pages=(
                settings["max_pages"]
            ),
            results_per_page=(
                settings["results_per_page"]
            )
        )

        logger.info(
            "Scheduled job search completed."
        )

        logger.info(
            f"Jobs found: "
            f"{result.get('total_jobs_found', 0)}"
        )

        logger.info(
            f"Jobs saved: "
            f"{result.get('jobs_saved', 0)}"
        )

        logger.info(
            f"Duplicates: "
            f"{result.get('duplicates', 0)}"
        )

        return result

    except Exception:

        logger.exception(
            "Scheduled job search failed."
        )

        return {
            "success": False,
            "error": (
                "Scheduled job search failed."
            )
        }

    finally:

        db.close()


# ============================================================
# STALE JOB CLEANUP
# ============================================================

def run_stale_job_cleanup():

    db = SessionLocal()

    try:

        settings = get_scheduler_settings()

        result = mark_stale_jobs(
            db=db,
            stale_after_hours=(
                settings[
                    "stale_after_hours"
                ]
            )
        )

        if isinstance(result, dict):

            stale_count = result.get(
                "stale_count",
                0
            )

            if stale_count > 0:

                logger.info(
                    "Stale-job cleanup: "
                    f"{stale_count} "
                    "job(s) marked stale."
                )

            else:

                logger.info(
                    "Stale-job cleanup completed. "
                    "No jobs marked stale."
                )

        return result

    except Exception:

        logger.exception(
            "Stale-job cleanup failed."
        )

        return {
            "success": False,
            "error": (
                "Stale-job cleanup failed."
            )
        }

    finally:

        db.close()


# ============================================================
# FOLLOW-UP PROCESSING
# ============================================================

def run_follow_up_processing():

    db = SessionLocal()

    try:

        result = process_due_follow_ups(
            db=db
        )

        processed_count = result.get(
            "processed_count",
            0
        )

        if processed_count > 0:

            logger.info(
                "Follow-up processing: "
                f"{processed_count} "
                "follow-up(s) are now due."
            )

        else:

            logger.info(
                "Follow-up processing completed. "
                "No follow-ups are due."
            )

        return result

    except Exception:

        logger.exception(
            "Follow-up processing failed."
        )

        return {
            "success": False,
            "processed_count": 0,
            "error": (
                "Follow-up processing failed."
            )
        }

    finally:

        db.close()


# ============================================================
# START SCHEDULER
# ============================================================

def start_scheduler():

    if scheduler.running:

        logger.info(
            "Scheduler is already running."
        )

        return

    settings = get_scheduler_settings()

    # --------------------------------------------------------
    # JOB SEARCH
    # --------------------------------------------------------

    scheduler.add_job(
        run_scheduled_job_search,
        "interval",
        hours=(
            settings[
                "search_interval_hours"
            ]
        ),
        id="scheduled_job_search",
        replace_existing=True
    )

    # --------------------------------------------------------
    # STALE JOB CLEANUP
    # --------------------------------------------------------

    if settings[
        "automatic_stale_cleanup"
    ]:

        scheduler.add_job(
            run_stale_job_cleanup,
            "interval",
            hours=24,
            id="stale_job_cleanup",
            replace_existing=True
        )

    # --------------------------------------------------------
    # FOLLOW-UP PROCESSING
    # --------------------------------------------------------

    if settings[
        "automatic_follow_up_processing"
    ]:

        scheduler.add_job(
            run_follow_up_processing,
            "interval",
            hours=1,
            id="outreach_follow_up_processor",
            replace_existing=True
        )

    scheduler.start()

    logger.info(
        "Scheduler started."
    )

    logger.info(
        "Job-search scheduler started."
    )

    logger.info(
        f"Search title: "
        f"{settings['search_title']}"
    )

    logger.info(
        f"Search location: "
        f"{settings['search_location']}"
    )

    logger.info(
        "Search interval: "
        f"{settings['search_interval_hours']} "
        "hours"
    )

    logger.info(
        f"Maximum pages: "
        f"{settings['max_pages']}"
    )

    logger.info(
        f"Results per page: "
        f"{settings['results_per_page']}"
    )

    logger.info(
        f"Stale after: "
        f"{settings['stale_after_hours']} "
        "hours"
    )

    logger.info(
        "Automatic stale-job cleanup: "
        f"{settings['automatic_stale_cleanup']}"
    )

    logger.info(
        "Automatic outreach follow-up "
        "processing: "
        f"{settings['automatic_follow_up_processing']}"
    )


# ============================================================
# STOP SCHEDULER
# ============================================================

def stop_scheduler():

    if not scheduler.running:

        logger.info(
            "Scheduler is not running."
        )

        return

    try:

        scheduler.shutdown(
            wait=False
        )

        logger.info(
            "Scheduler stopped."
        )

    except Exception:

        logger.exception(
            "Error while stopping scheduler."
        )