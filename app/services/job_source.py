import json
import time

from pathlib import Path
from typing import List, Dict, Optional

import requests

from app.services.logger import logger

from app.services.config_validator import (
    get_configuration
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


def load_candidate_profile():

    with open(
        PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def normalize_job_type(
    contract_type
):

    if not contract_type:
        return None

    normalized = (
        str(contract_type)
        .strip()
        .lower()
    )

    if normalized in [
        "permanent",
        "full-time",
        "full time"
    ]:
        return "Full-time"

    if normalized in [
        "contract",
        "contractor"
    ]:
        return "Contract"

    if normalized in [
        "part-time",
        "part time"
    ]:
        return "Part-time"

    if normalized in [
        "temporary"
    ]:
        return "Temporary"

    if normalized in [
        "internship",
        "intern"
    ]:
        return "Internship"

    return str(
        contract_type
    ).strip()


def fetch_jobs(
    search_title: Optional[str] = None,
    search_location: Optional[str] = None,
    max_pages: Optional[int] = None,
    results_per_page: Optional[int] = None
) -> List[Dict]:

    # ========================================================
    # LOAD CENTRALIZED CONFIGURATION
    # ========================================================

    configuration = get_configuration()

    app_id = configuration[
        "adzuna_app_id"
    ]

    app_key = configuration[
        "adzuna_app_key"
    ]

    if not app_id:

        logger.error(
            "ADZUNA_APP_ID is not configured"
        )

        print(
            "ERROR: ADZUNA_APP_ID is not configured."
        )

        return []

    if not app_key:

        logger.error(
            "ADZUNA_APP_KEY is not configured"
        )

        print(
            "ERROR: ADZUNA_APP_KEY is not configured."
        )

        return []

    # ========================================================
    # LOAD CANDIDATE PROFILE
    # ========================================================

    candidate = load_candidate_profile()

    preferences = candidate.get(
        "preferences",
        {}
    )

    job_titles = preferences.get(
        "job_titles",
        []
    )

    locations = preferences.get(
        "locations",
        []
    )

    # ========================================================
    # DEFAULT SEARCH VALUES
    # ========================================================

    if not search_title:

        search_title = configuration[
            "job_search_title"
        ]

        if not search_title:

            search_title = (
                job_titles[0]
                if job_titles
                else "Java Developer"
            )

    if not search_location:

        search_location = configuration[
            "job_search_location"
        ]

        if not search_location:

            search_location = (
                locations[0]
                if locations
                else "Hyderabad"
            )

    # ========================================================
    # SEARCH PAGINATION SETTINGS
    # ========================================================

    if max_pages is None:

        max_pages = configuration[
            "job_search_max_pages"
        ]

    if results_per_page is None:

        results_per_page = configuration[
            "job_search_results_per_page"
        ]

    max_pages = max(
        1,
        min(
            int(max_pages),
            10
        )
    )

    results_per_page = max(
        1,
        min(
            int(results_per_page),
            50
        )
    )

    logger.info(
        f"Starting Adzuna job search: "
        f"title={search_title}, "
        f"location={search_location}, "
        f"pages={max_pages}, "
        f"results_per_page={results_per_page}"
    )

    all_jobs = []

    seen_urls = set()

    max_retries = 3

    # ========================================================
    # ADZUNA PAGINATED SEARCH
    # ========================================================

    for page in range(
        1,
        max_pages + 1
    ):

        api_url = (
            "https://api.adzuna.com/"
            f"v1/api/jobs/in/search/{page}"
        )

        params = {
            "app_id": app_id,
            "app_key": app_key,
            "results_per_page": (
                results_per_page
            ),
            "what": search_title,
            "where": search_location,
            "content-type": "application/json"
        }

        data = None

        # ====================================================
        # RETRY LOGIC
        # ====================================================

        for attempt in range(
            1,
            max_retries + 1
        ):

            try:

                logger.info(
                    f"Adzuna request: "
                    f"page={page}, "
                    f"attempt={attempt}"
                )

                response = requests.get(
                    api_url,
                    params=params,
                    timeout=20
                )

                response.raise_for_status()

                data = response.json()

                logger.info(
                    f"Adzuna request successful: "
                    f"page={page}, "
                    f"attempt={attempt}"
                )

                break

            except requests.Timeout as error:

                logger.warning(
                    f"Adzuna timeout: "
                    f"page={page}, "
                    f"attempt={attempt}: "
                    f"{error}"
                )

            except requests.HTTPError as error:

                status_code = (
                    error.response.status_code
                    if error.response is not None
                    else None
                )

                logger.warning(
                    f"Adzuna HTTP error: "
                    f"page={page}, "
                    f"attempt={attempt}, "
                    f"status={status_code}"
                )

                if (
                    status_code is not None
                    and 400 <= status_code < 500
                    and status_code != 429
                ):

                    logger.error(
                        "Adzuna returned a "
                        "non-retryable HTTP error: "
                        f"{status_code}"
                    )

                    break

            except requests.RequestException as error:

                logger.warning(
                    f"Adzuna request failed: "
                    f"page={page}, "
                    f"attempt={attempt}: "
                    f"{error}"
                )

            except ValueError as error:

                logger.warning(
                    f"Adzuna returned invalid JSON: "
                    f"page={page}, "
                    f"attempt={attempt}: "
                    f"{error}"
                )

                break

            # =================================================
            # EXPONENTIAL BACKOFF
            # =================================================

            if attempt < max_retries:

                wait_seconds = (
                    2 ** (attempt - 1)
                )

                logger.info(
                    f"Retrying Adzuna request "
                    f"in {wait_seconds} seconds"
                )

                time.sleep(
                    wait_seconds
                )

        # ====================================================
        # PAGE FAILED
        # ====================================================

        if data is None:

            logger.error(
                f"Adzuna page {page} failed "
                f"after {max_retries} attempts"
            )

            print(
                f"Adzuna page {page} "
                "failed after retries."
            )

            continue

        # ====================================================
        # PROCESS RESULTS
        # ====================================================

        results = data.get(
            "results",
            []
        )

        logger.info(
            f"Adzuna page {page}: "
            f"{len(results)} jobs found"
        )

        print(
            f"Page {page}: "
            f"{len(results)} jobs found"
        )

        for job in results:

            company = job.get(
                "company",
                {}
            )

            location = job.get(
                "location",
                {}
            )

            job_url = job.get(
                "redirect_url",
                ""
            )

            # =================================================
            # URL VALIDATION
            # =================================================

            if not job_url:

                logger.warning(
                    "Skipping Adzuna job "
                    "because URL is missing"
                )

                continue

            # =================================================
            # DUPLICATE URL PROTECTION
            # =================================================

            if job_url in seen_urls:

                continue

            seen_urls.add(
                job_url
            )

            # =================================================
            # JOB TYPE NORMALIZATION
            # =================================================

            job_type = normalize_job_type(
                job.get(
                    "contract_type"
                )
            )

            # =================================================
            # SAVE NORMALIZED JOB
            # =================================================

            all_jobs.append(
                {
                    "title": job.get(
                        "title",
                        ""
                    ),

                    "company": company.get(
                        "display_name",
                        "Unknown Company"
                    ),

                    "location": location.get(
                        "display_name",
                        search_location
                    ),

                    "description": job.get(
                        "description",
                        ""
                    ),

                    "source": "Adzuna",

                    "url": job_url,

                    "salary_min": job.get(
                        "salary_min"
                    ),

                    "salary_max": job.get(
                        "salary_max"
                    ),

                    "job_type": job_type
                }
            )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    logger.info(
        f"Total unique jobs fetched "
        f"from Adzuna: {len(all_jobs)}"
    )

    print(
        f"Total unique jobs fetched: "
        f"{len(all_jobs)}"
    )

    return all_jobs