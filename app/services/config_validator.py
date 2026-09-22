import os

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

ENV_FILE = (
    PROJECT_ROOT / ".env"
)


load_dotenv(
    ENV_FILE
)


def get_environment_variable(
    name: str,
    default=None
):
    """
    Read an environment variable.

    Returns the default value when the
    variable is not configured.
    """

    value = os.getenv(name)

    if value is None:
        return default

    value = value.strip()

    if not value:
        return default

    return value


def get_integer_environment_variable(
    name: str,
    default: int
):
    """
    Read an integer environment variable.

    Falls back to the supplied default when
    the value is missing or invalid.
    """

    value = get_environment_variable(
        name
    )

    if value is None:
        return default

    try:
        return int(value)

    except ValueError:

        return default


def get_float_environment_variable(
    name: str,
    default: float
):
    """
    Read a floating-point environment variable.

    Falls back to the supplied default when
    the value is missing or invalid.
    """

    value = get_environment_variable(
        name
    )

    if value is None:
        return default

    try:
        return float(value)

    except ValueError:

        return default


def get_boolean_environment_variable(
    name: str,
    default: bool = False
):
    """
    Read a boolean environment variable.
    """

    value = get_environment_variable(
        name
    )

    if value is None:
        return default

    normalized = (
        value
        .strip()
        .lower()
    )

    if normalized in {
        "true",
        "1",
        "yes",
        "y",
        "on"
    }:
        return True

    if normalized in {
        "false",
        "0",
        "no",
        "n",
        "off"
    }:
        return False

    return default


def get_configuration():
    """
    Return application configuration.

    Sensitive values such as API keys are read
    from environment variables and are not stored
    directly in the source code.
    """

    configuration = {

        "adzuna_app_id": (
            get_environment_variable(
                "ADZUNA_APP_ID"
            )
        ),

        "adzuna_app_key": (
            get_environment_variable(
                "ADZUNA_APP_KEY"
            )
        ),

        "job_search_title": (
            get_environment_variable(
                "JOB_SEARCH_TITLE",
                "Java Developer"
            )
        ),

        "job_search_location": (
            get_environment_variable(
                "JOB_SEARCH_LOCATION",
                "Hyderabad"
            )
        ),

        "job_search_interval_hours": (
            get_float_environment_variable(
                "JOB_SEARCH_INTERVAL_HOURS",
                6.0
            )
        ),

        "job_search_max_pages": (
            get_integer_environment_variable(
                "JOB_SEARCH_MAX_PAGES",
                1
            )
        ),

        "job_search_results_per_page": (
            get_integer_environment_variable(
                "JOB_SEARCH_RESULTS_PER_PAGE",
                10
            )
        ),

        "job_stale_after_hours": (
            get_float_environment_variable(
                "JOB_STALE_AFTER_HOURS",
                72.0
            )
        ),

        "application_daily_limit": (
            get_integer_environment_variable(
                "APPLICATION_DAILY_LIMIT",
                10
            )
        ),

        "application_portal_limit": (
            get_integer_environment_variable(
                "APPLICATION_PORTAL_LIMIT",
                5
            )
        ),

        "automatic_stale_cleanup": (
            get_boolean_environment_variable(
                "AUTOMATIC_STALE_CLEANUP",
                True
            )
        ),

        "automatic_follow_up_processing": (
            get_boolean_environment_variable(
                "AUTOMATIC_FOLLOW_UP_PROCESSING",
                True
            )
        )
    }

    return configuration


def validate_configuration():
    """
    Validate required configuration.

    API credentials are currently optional because
    the application can still start when the external
    job source is not configured.
    """

    configuration = get_configuration()

    errors = []
    warnings = []

    if (
        configuration[
            "job_search_interval_hours"
        ] <= 0
    ):

        errors.append(
            "JOB_SEARCH_INTERVAL_HOURS must be greater than 0."
        )

    if (
        configuration[
            "job_search_max_pages"
        ] < 1
    ):

        errors.append(
            "JOB_SEARCH_MAX_PAGES must be at least 1."
        )

    if (
        configuration[
            "job_search_results_per_page"
        ] < 1
    ):

        errors.append(
            "JOB_SEARCH_RESULTS_PER_PAGE must be at least 1."
        )

    if (
        configuration[
            "job_stale_after_hours"
        ] <= 0
    ):

        errors.append(
            "JOB_STALE_AFTER_HOURS must be greater than 0."
        )

    if (
        configuration[
            "application_daily_limit"
        ] < 1
    ):

        errors.append(
            "APPLICATION_DAILY_LIMIT must be at least 1."
        )

    if (
        configuration[
            "application_portal_limit"
        ] < 1
    ):

        errors.append(
            "APPLICATION_PORTAL_LIMIT must be at least 1."
        )

    if not configuration["adzuna_app_id"]:

        warnings.append(
            "ADZUNA_APP_ID is not configured."
        )

    if not configuration["adzuna_app_key"]:

        warnings.append(
            "ADZUNA_APP_KEY is not configured."
        )

    if errors:

        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "configuration": {
                key: value
                for key, value in configuration.items()
                if "key" not in key
                and "id" not in key
            }
        }

    return {
        "valid": True,
        "errors": [],
        "warnings": warnings,
        "configuration": {
            key: value
            for key, value in configuration.items()
            if "key" not in key
            and "id" not in key
        }
    }