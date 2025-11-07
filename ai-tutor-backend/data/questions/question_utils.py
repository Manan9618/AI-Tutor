# data/questions/question_utils.py
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.utils.logger import get_logger

logger = get_logger("question_utils")

# Define base directories
BASE_DIR = Path("data/questions")
HISTORY_DIR = BASE_DIR / "history"
SAMPLES_DIR = BASE_DIR / "samples"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

def save_quiz(topic: str, level: str, questions: List[Dict[str, Any]]) -> Path:
    """
    Save generated quiz questions to a timestamped JSON file.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{topic.lower().replace(' ', '_')}_{level}_{timestamp}.json"
        file_path = HISTORY_DIR / filename
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(questions, f, ensure_ascii=False, indent=4)
        
        logger.info(f"✅ Quiz saved successfully: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"❌ Failed to save quiz: {e}")
        raise

def load_quiz(file_path: str | Path) -> Optional[List[Dict[str, Any]]]:
    """
    Load quiz data from a JSON file.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"⚠ Quiz file not found: {file_path}")
            return None
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        logger.info(f"✅ Loaded quiz: {file_path}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in quiz file {file_path}: {e}")
        return None

def list_quizzes() -> List[str]:
    """
    List all stored quizzes in the history directory.
    """
    try:
        quizzes = [f.name for f in HISTORY_DIR.glob("*.json")]
        logger.info(f"📄 Found {len(quizzes)} stored quizzes.")
        return quizzes
    except Exception as e:
        logger.error(f"❌ Error listing quizzes: {e}")
        return []

def get_latest_quiz() -> Optional[Path]:
    """
    Get the most recently saved quiz file.
    """
    try:
        files = sorted(HISTORY_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        return files[0] if files else None
    except Exception as e:
        logger.error(f"❌ Error fetching latest quiz: {e}")
        return None
