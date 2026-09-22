import os

from app.services.logger import logger


def validate_configuration():

    errors = []

    warnings = []

    # Adzuna configuration
    if not os.getenv("ADZUNA_APP_ID"):
        errors.append(
            "ADZUNA_APP_ID is missing"
        )

    if not os.getenv("ADZUNA_APP_KEY"):
        errors.append(
            "ADZUNA_APP_KEY is missing"
        )

    # Job search configuration
    search_title = os.getenv(
        "JOB_SEARCH_TITLE"
    )

    if not search_title:
        warnings.append(
            "JOB_SEARCH_TITLE is not configured"
        )

    search_location = os.getenv(
        "JOB_SEARCH_LOCATION"
    )

    if not search_location:
        warnings.append(
            "JOB_SEARCH_LOCATION is not configured"
        )

    # Numeric configuration
    numeric_settings = {
        "JOB_SEARCH_INTERVAL_HOURS": 6,
        "JOB_SEARCH_MAX_PAGES": 1,
        "JOB_SEARCH_RESULTS_PER_PAGE": 10,
        "JOB_STALE_AFTER_HOURS": 72
    }

    for setting, default_value in (
        numeric_settings.items()
    ):

        value = os.getenv(setting)

        if value is None:
            warnings.append(
                f"{setting} is not configured; "
                f"default {default_value} will be used"
            )

            continue

        try:

            numeric_value = float(value)

            if numeric_value <= 0:
                errors.append(
                    f"{setting} must be greater than 0"
                )

        except ValueError:

            errors.append(
                f"{setting} must be numeric"
            )

    if errors:

        logger.error(
            "Configuration validation failed"
        )

        for error in errors:

            logger.error(
                f"Configuration error: {error}"
            )

    else:

        logger.info(
            "Configuration validation passed"
        )

    for warning in warnings:

        logger.warning(
            f"Configuration warning: {warning}"
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }