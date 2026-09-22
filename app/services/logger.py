import logging
from pathlib import Path


PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


LOG_DIRECTORY = (
    PROJECT_ROOT / "data" / "logs"
)

LOG_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)


LOG_FILE = (
    LOG_DIRECTORY / "application.log"
)


logging.basicConfig(
    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),

    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),

        logging.StreamHandler()
    ]
)


logger = logging.getLogger(
    "autonomous_job_agent"
)