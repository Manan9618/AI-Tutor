"""
Writes and updates content files and metadata for the AI Tutor.
"""
import json
from pathlib import Path
from typing import Dict
from datetime import datetime

CONTENT_DIR = Path(__file__).resolve().parent
METADATA_PATH = CONTENT_DIR / "metadata.json"

def save_content(content_id: str, text: str, title: str, tags: list):
    """Save new learning content."""
    file_path = CONTENT_DIR / f"{content_id}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    metadata = {}
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    metadata[content_id] = {
        "title": title,
        "tags": tags,
        "filename": f"{content_id}.txt",
        "created_at": datetime.utcnow().isoformat()
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
