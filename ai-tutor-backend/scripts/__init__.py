# scripts/__init__.py
"""
Utility scripts for managing content, questions, logs, and embeddings.
This makes the `scripts` directory a valid Python package.
"""

from pathlib import Path
from app.utils.logger import get_logger

# Setup logger for the scripts package
logger = get_logger("scripts")

# Ensure base data folders exist
DATA_DIR = Path("data")
for subdir in ["content/explanation", "content/embeddings", "logs", "questions"]:
    path = DATA_DIR / subdir
    path.mkdir(parents=True, exist_ok=True)

logger.info("📦 Scripts package initialized successfully.")
