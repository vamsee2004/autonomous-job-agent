import os

from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from dotenv import load_dotenv

from app.database.connection import SessionLocal

from app.services.automated_job_pipeline import (
    run_job_search_pipeline
)

from app.services.job_lifecycle import (
    mark_stale_jobs
)

from app.services.logger import logger


load_dotenv()


scheduler = BackgroundScheduler()


def get_scheduler_settings():

    search_title = os.getenv(
        "JOB_SEARCH_TITLE",
        "Java Developer"
    )

    search_location = os.getenv(
        "JOB_SEARCH_LOCATION",
        "Hyderabad"
    )

    try:
        interval_hours = float(
            os.getenv(
                "JOB_SEARCH_INTERVAL_HOURS",
                "6"
            )
        )
    except ValueError:
        interval_hours = 6

    try:
        max_pages = int(
            os.getenv(
                "JOB_SEARCH_MAX_PAGES",
                "1"
            )
        )
    except ValueError:
        max_pages = 1

    try:
        results_per_page = int(
            os.getenv(
                "JOB_SEARCH_RESULTS_PER_PAGE",
                "10"
            )
        )
    except ValueError:
        results_per_page = 10

    try:
        stale_after_hours = int(
            os.getenv(
                "JOB_STALE_AFTER_HOURS",
                "72"
            )
        )
    except ValueError:
        stale_after_hours = 72

    return {
        "search_title": search_title,
        "search_location": search_location,
        "interval_hours": max(
            interval_hours,
            1
        ),
        "max_pages": max(
            max_pages,
            1
        ),
        "results_per_page": max(
            results_per_page,
            1
        ),
        "stale_after_hours": max(
            stale_after_hours,
            1
        )
    }


def run_stale_job_cleanup():

    settings = get_scheduler_settings()

    db = SessionLocal()

    try:

        result = mark_stale_jobs(
            db=db,
            stale_after_hours=(
                settings[
                    "stale_after_hours"
                ]
            )
        )

        logger.info(
            "Stale-job cleanup completed: "
            f"{result.get('jobs_marked_stale', 0)} "
            "jobs marked stale"
        )

        print(
            "Stale-job cleanup completed."
        )

        print(
            f"Jobs checked: "
            f"{result.get('jobs_checked', 0)}"
        )

        print(
            f"Jobs marked stale: "
            f"{result.get('jobs_marked_stale', 0)}"
        )

    except Exception as error:

        logger.exception(
            f"Stale-job cleanup failed: {error}"
        )

        print(
            "Stale-job cleanup failed:"
        )

        print(error)

    finally:

        db.close()


def run_scheduled_job_search():

    settings = get_scheduler_settings()

    db = SessionLocal()

    try:

        result = run_job_search_pipeline(
            db=db,
            search_title=settings[
                "search_title"
            ],
            search_location=settings[
                "search_location"
            ],
            max_pages=settings[
                "max_pages"
            ],
            results_per_page=settings[
                "results_per_page"
            ]
        )

        logger.info(
            "Scheduled job search completed: "
            f"pipeline_run_id="
            f"{result.get('pipeline_run_id')}, "
            f"status="
            f"{result.get('pipeline_run_status')}"
        )

        print(
            "Scheduled job search completed."
        )

        print(
            f"Pipeline run ID: "
            f"{result.get('pipeline_run_id')}"
        )

        print(
            f"Pipeline status: "
            f"{result.get('pipeline_run_status')}"
        )

        if result.get("success"):

            search_summary = result.get(
                "search_summary",
                {}
            )

            print(
                f"Search title: "
                f"{settings['search_title']}"
            )

            print(
                f"Search location: "
                f"{settings['search_location']}"
            )

            print(
                f"Jobs found: "
                f"{search_summary.get(
                    'total_jobs_found',
                    0
                )}"
            )

            print(
                f"Jobs saved: "
                f"{search_summary.get(
                    'jobs_saved',
                    0
                )}"
            )

            print(
                f"Applications prepared: "
                f"{result.get(
                    'applications_prepared',
                    0
                )}"
            )

        else:

            print(
                "Pipeline returned an error:"
            )

            print(
                result.get(
                    "error",
                    "Unknown error"
                )
            )

    except Exception as error:

        logger.exception(
            f"Scheduled job search failed: {error}"
        )

        print(
            "Scheduled job search failed:"
        )

        print(error)

    finally:

        db.close()


def start_scheduler():

    if scheduler.running:

        return

    settings = get_scheduler_settings()

    scheduler.add_job(
        run_scheduled_job_search,
        trigger="interval",
        hours=settings[
            "interval_hours"
        ],
        id="job_search_pipeline",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.add_job(
        run_stale_job_cleanup,
        trigger="interval",
        hours=settings[
            "interval_hours"
        ],
        id="stale_job_cleanup",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()

    logger.info(
        "Job-search scheduler started"
    )

    print(
        "Job-search scheduler started."
    )

    print(
        f"Search title: "
        f"{settings['search_title']}"
    )

    print(
        f"Search location: "
        f"{settings['search_location']}"
    )

    print(
        f"Search interval: "
        f"{settings['interval_hours']} hours"
    )

    print(
        f"Maximum pages: "
        f"{settings['max_pages']}"
    )

    print(
        f"Results per page: "
        f"{settings['results_per_page']}"
    )

    print(
        f"Stale after: "
        f"{settings['stale_after_hours']} hours"
    )

    print(
        "Automatic stale-job cleanup enabled."
    )


def stop_scheduler():

    if scheduler.running:

        scheduler.shutdown()

        logger.info(
            "Job-search scheduler stopped"
        )

        print(
            "Job-search scheduler stopped."
        )