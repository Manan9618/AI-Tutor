# app/utils/logger.py
from loguru import logger
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False
):
    """
    Configure Loguru with JSON and console logging.
    Creates separate logs for app, error, and access tracking.
    """
    # Remove any default handlers
    logger.remove()

    # --- Define log directory ---
    LOG_DIR = Path("data/logs")
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # --- Define base log format ---
    format_str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ) if not json_format else (
        "{{\"time\": \"{time:YYYY-MM-DD HH:mm:ss.SSS}\", "
        "\"level\": \"{level}\", "
        "\"module\": \"{name}\", "
        "\"function\": \"{function}\", "
        "\"line\": {line}, "
        "\"message\": \"{message}\"}}"
    )

    # --- Console handler ---
    logger.add(
        sys.stderr,
        level=log_level.upper(),
        format=format_str,
        colorize=not json_format,
        enqueue=True
    )

    # --- App log file handler ---
    app_log_file = log_file or (LOG_DIR / "app.log")
    logger.add(
        app_log_file,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level=log_level.upper(),
        serialize=json_format,
        enqueue=True
    )

    # --- Error log file handler ---
    error_log_file = LOG_DIR / "error.log"
    logger.add(
        error_log_file,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        level="ERROR",
        serialize=json_format,
        enqueue=True
    )

    # --- Access log file (optional for API requests) ---
    access_log_file = LOG_DIR / "access.log"
    logger.add(
        access_log_file,
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        level="INFO",
        filter=lambda record: "ACCESS" in record["extra"],
        serialize=json_format,
        enqueue=True
    )


def get_logger(name: str = "ai_tutor"):
    """
    Get a named logger instance bound with context.
    Example:
        logger = get_logger("main")
        logger.info("Starting app...")
    """
    return logger.bind(name=name)


# --- Initialize global logger configuration ---
LOG_DIR = Path("data/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

setup_logging(
    log_level="INFO",
    log_file=LOG_DIR / "app.log",
    json_format=True
)
