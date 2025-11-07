# data/scripts/init_data.py
import os
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger("init_data")

def initialize_directories():
    """
    Create required directories for logs, content, and questions.
    """
    base_dirs = [
        Path("data/logs"),
        Path("data/content/explanation"),
        Path("data/questions/history"),
    ]

    for directory in base_dirs:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Ensured directory exists: {directory}")

def initialize_env():
    """
    Ensure the .env file exists with basic environment variables.
    """
    env_path = Path(".env")
    if not env_path.exists():
        logger.info("⚙️ Creating default .env file...")
        env_path.write_text(
            "OPENAI_API_KEY=\n"
            "DATABASE_URL=sqlite+aiosqlite:///./data/ai_tutor.db\n"
            "SECRET_KEY=your_secret_key_here\n"
        )
        logger.info("✅ Default .env file created successfully.")
    else:
        logger.info("ℹ️ .env file already exists.")

if __name__ == "__main__":
    logger.info("🚀 Initializing AI Tutor environment...")
    initialize_directories()
    initialize_env()
    logger.info("✅ Environment setup completed successfully.")
