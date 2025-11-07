# scripts/backup_logs.py
from pathlib import Path
import zipfile
from datetime import datetime
from app.utils.logger import get_logger

logger = get_logger("backup_logs")

def backup_logs():
    logs_dir = Path("data/logs")
    backup_dir = Path("data/backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    backup_file = backup_dir / f"logs_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"

    with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in logs_dir.glob("*.log"):
            zipf.write(file, file.name)
            logger.info(f"📦 Added {file.name} to backup")

    logger.info(f"✅ Logs backed up successfully at {backup_file}")

if __name__ == "__main__":
    backup_logs()
