import logging
import sys
from backend.app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configure application-wide structured logger."""
    log_level = getattr(logging, settings.BACKEND_LOG_LEVEL.upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger("sih26191")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
