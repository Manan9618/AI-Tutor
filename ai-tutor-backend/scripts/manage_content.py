# scripts/manage_content.py
import json
from pathlib import Path
from app.utils.logger import get_logger

logger = get_logger("manage_content")

EXPLANATION_DIR = Path("data/content/explanation")

def add_content(topic: str, content: str):
    """Add new explanation content."""
    file_path = EXPLANATION_DIR / f"{topic.replace(' ', '_')}.json"
    data = {"topic": topic, "content": content}

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Added new content for topic: {topic}")


def list_content():
    """List all existing topics."""
    files = [f.stem for f in EXPLANATION_DIR.glob("*.json")]
    logger.info(f"📚 Available topics: {files}")
    return files


if __name__ == "__main__":
    add_content("Artificial Intelligence", "AI is the simulation of human intelligence by machines.")
    list_content()
