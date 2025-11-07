# app/__init__.py
"""
AI Tutor Backend package initialization.
"""

from app.config import settings
from app.utils.logger import get_logger, setup_logging

# Initialize global logging on import
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    json_format=True
)

logger = get_logger("app")

__all__ = ["settings", "logger"]
