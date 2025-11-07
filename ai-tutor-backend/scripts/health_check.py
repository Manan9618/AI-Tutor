# scripts/health_check.py
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger("health_check")

def health_check():
    paths = {
        "Explanations": Path("data/content/explanation"),
        "Embeddings": Path("data/content/embeddings"),
        "Logs": Path("data/logs"),
        "Questions": Path("data/questions"),
    }

    logger.info("🩺 Performing system health check...")
    for name, path in paths.items():
        if path.exists() and any(path.iterdir()):
            logger.info(f"✅ {name} directory OK: {len(list(path.iterdir()))} files found.")
        else:
            logger.warning(f"⚠️ {name} directory missing or empty: {path}")

if __name__ == "__main__":
    health_check()
