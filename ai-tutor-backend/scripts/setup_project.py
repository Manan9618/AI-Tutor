# scripts/setup_project.py
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger("setup_project")

def setup_directories():
    """Create all required folders for the app and data layers."""
    folders = [
        "data/content/explanation",
        "data/content/embeddings",
        "data/logs",
        "data/questions",
        "data/scripts",
    ]
    for folder in folders:
        path = Path(folder)
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📂 Created folder: {path}")

    logger.info("✅ All required directories initialized successfully.")


if __name__ == "__main__":
    setup_directories()
