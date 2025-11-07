"""
Handles saving and retrieving AI-generated explanations.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

EXPLANATION_PATH = Path(__file__).resolve().parent / "sample_explanations.json"

def save_explanation(topic: str, content: str):
    """Save explanation to local JSON storage."""
    data = {}
    if EXPLANATION_PATH.exists():
        with open(EXPLANATION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

    data[topic] = {
        "explanation": content,
        "timestamp": datetime.utcnow().isoformat()
    }

    with open(EXPLANATION_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_explanation(topic: str) -> Optional[str]:
    """Retrieve explanation by topic."""
    if not EXPLANATION_PATH.exists():
        return None

    with open(EXPLANATION_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    entry = data.get(topic)
    return entry.get("explanation") if entry else None
