# data/scripts/maintenance.py
import os
from pathlib import Path
from datetime import datetime, timedelta
from app.utils.logger import get_logger

logger = get_logger("maintenance")

def cleanup_logs(days: int = 7):
    """Delete log files older than X days."""
    log_dir = Path("data/logs")
    if not log_dir.exists():
        logger.warning("⚠️ Log directory not found.")
        return

    now = datetime.now()
    for log_file in log_dir.glob("*.zip"):
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        if (now - mtime) > timedelta(days=days):
            log_file.unlink(missing_ok=True)
            logger.info(f"🧹 Deleted old log file: {log_file}")

def cleanup_quizzes(days: int = 30):
    """Remove quiz JSON files older than X days."""
    quiz_dir = Path("data/questions/history")
    if not quiz_dir.exists():
        logger.warning("⚠️ Quiz history directory not found.")
        return

    now = datetime.now()
    for quiz_file in quiz_dir.glob("*.json"):
        mtime = datetime.fromtimestamp(quiz_file.stat().st_mtime)
        if (now - mtime) > timedelta(days=days):
            quiz_file.unlink(missing_ok=True)
            logger.info(f"🧹 Deleted old quiz file: {quiz_file}")

if __name__ == "__main__":
    logger.info("🧹 Running maintenance cleanup...")
    cleanup_logs()
    cleanup_quizzes()
    logger.info("✅ Maintenance tasks completed.")
