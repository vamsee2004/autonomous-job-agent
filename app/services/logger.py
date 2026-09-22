import logging

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


LOG_DIRECTORY = (
    PROJECT_ROOT
    / "data"
    / "logs"
)


LOG_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


LOG_FILE = (
    LOG_DIRECTORY
    / "application.log"
)


# ============================================================
# LOGGER SETTINGS
# ============================================================

LOGGER_NAME = (
    "autonomous_job_agent"
)

LOG_LEVEL = logging.INFO


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


# ============================================================
# LOGGER CREATION
# ============================================================

logger = logging.getLogger(
    LOGGER_NAME
)


logger.setLevel(
    LOG_LEVEL
)


logger.propagate = False


# ============================================================
# PREVENT DUPLICATE HANDLERS
# ============================================================

if not logger.handlers:

    file_handler = (
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        )
    )

    console_handler = (
        logging.StreamHandler()
    )

    formatter = (
        logging.Formatter(
            LOG_FORMAT
        )
    )

    file_handler.setFormatter(
        formatter
    )

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def log_exception(
    message: str
):
    """
    Log an exception with traceback details.
    """

    logger.exception(
        message
    )


def log_error(
    message: str
):
    """
    Log an error message.
    """

    logger.error(
        message
    )


def log_warning(
    message: str
):
    """
    Log a warning message.
    """

    logger.warning(
        message
    )


def log_info(
    message: str
):
    """
    Log an informational message.
    """

    logger.info(
        message
    )